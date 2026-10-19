"""Seed data: the starting content of the entities a product shows to its audience.

A public site shows offerings, credentials, testimonials and the like, content the business authors and the audience
never creates. Without records the page has nothing to show (an owner-only entity stays empty forever on a site with no
owner screens), and the model would invent the content as literals inside the UI. Instead this stage asks for sample
records once, proves each one against the generated domain class and response schema, and writes
`src/seed_data.json`; the generated routers load that file at startup, so the interface renders real data from the API
that the business can edit later.

Retry policy (.claude/rules/pipeline.md): the domain verdict on a rejected record is fed back for exactly one more
attempt; provider and parse errors are never retried.
"""

import json
import os
import subprocess
import sys
import time
import run_options
from datetime import date
from typing import Any, Dict, List, Optional

import agent_orchestrator
from onboarding.intent import ProductIntent, intent_block
from onboarding.router_engine import BusinessSpec, DomainStructureSchema
from onboarding.skeleton_builder import to_snake_case
from pipeline_trace import traced

SEED_FILE = os.path.join("src", "seed_data.json")
MAX_ATTEMPTS = 2  # first attempt + one verdict-fed retry

# Run inside the generated workspace: builds each record with the domain class and serialises it through the
# response schema, exactly as the router will, and prints the rejections as a JSON list.
_CHECK_SCRIPT = """
import json, sys
from importlib import import_module

payload = json.load(sys.stdin)
errors = []
for name, spec in payload.items():
    domain = getattr(import_module("src.domain." + spec["slug"]), name)
    schema = getattr(import_module("src.entrypoints.schemas"), name + "ResponseSchema")
    for index, record in enumerate(spec["records"]):
        try:
            schema(**domain(**record).to_dict())
        except Exception as exc:
            errors.append("%s[%d] (%s): %s: %s" % (name, index, record.get("id"), type(exc).__name__, exc))
print(json.dumps(errors))
"""


def _entity_block(structure: DomainStructureSchema) -> str:
    lines = []
    for ent in structure.shown_entities():
        attrs = ", ".join(f"{a.describe()}{'' if a.required else ' (optional)'}" for a in ent.attributes)
        lines.append(f"- **{ent.name}**: [{attrs}]")
    return "\n".join(lines)


def _rules_block(structure: DomainStructureSchema, inbox_specs: List[BusinessSpec]) -> str:
    shown = {e.name for e in structure.shown_entities()}
    rules = [f"- ({s.target_aggregate}) {s.given_when_then}" for s in inbox_specs if s.target_aggregate in shown]
    return "\n".join(rules) or "- (no rules specific to these entities)"


def check_records(workspace_dir: str, structure: DomainStructureSchema, records: Dict[str, List[Dict[str, Any]]]) -> List[str]:
    """Builds every record with the generated domain class; returns one message per rejected record."""
    payload = {name: {"slug": to_snake_case(name), "records": recs} for name, recs in records.items()}
    result = subprocess.run([sys.executable, "-c", _CHECK_SCRIPT], cwd=workspace_dir, input=json.dumps(payload),
                            capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        raise RuntimeError(f"the record check could not run: {result.stderr.strip()[-500:]}")
    return json.loads(result.stdout.strip().splitlines()[-1])


def _read_records(raw: str, expected: List[str]) -> Dict[str, List[Dict[str, Any]]]:
    records = agent_orchestrator.extract_json_object(raw).get("records")
    if not isinstance(records, dict):
        raise ValueError("the answer has no `records` object")
    missing = [name for name in expected if not isinstance(records.get(name), list) or not records[name]]
    if missing:
        raise ValueError(f"no records for: {', '.join(missing)}")
    unknown = [name for name in records if name not in expected]
    if unknown:
        raise ValueError(f"records for entities that are not shown to the audience: {', '.join(unknown)}")
    for name, recs in records.items():
        if not all(isinstance(r, dict) for r in recs):
            raise ValueError(f"{name} records must be JSON objects")
    return records


@traced("seed.synthesize")
def synthesize_seed_data(
    pitch: str,
    structure: DomainStructureSchema,
    inbox_specs: List[BusinessSpec],
    workspace_dir: str,
    intent: Optional[ProductIntent] = None,
) -> Dict[str, Any]:
    """Writes `src/seed_data.json` for the entities shown to the audience. Returns {success, skipped, error, files, attempts}."""
    start = time.time()
    shown = structure.shown_entities()
    if not shown:
        return {"success": True, "skipped": "no entity is shown to the audience", "files": [], "attempts": [],
                "elapsed_seconds": 0.0}
    expected = [e.name for e in shown]
    attempts: List[Dict[str, Any]] = []
    feedback = ""

    def failed(reason: str) -> Dict[str, Any]:
        print(f"[Compiler:Seed] Seed data failed: {reason}", flush=True)
        return {"success": False, "error": reason, "files": [], "attempts": attempts,
                "elapsed_seconds": round(time.time() - start, 2)}

    for number in range(1, run_options.attempts(MAX_ATTEMPTS) + 1):
        prompt = agent_orchestrator.load_prompt("seed_data.md", {
            "pitch": pitch, "intent_block": intent_block(intent), "entities_block": _entity_block(structure),
            "rules_block": _rules_block(structure, inbox_specs), "feedback_block": feedback,
            "today": date.today().isoformat(),
        })
        raw = agent_orchestrator.call_gemini(prompt, stage="seed_data", json_mode=True)
        if not raw or not raw.strip():
            return failed(agent_orchestrator.LAST_LLM_ERROR or "the LLM returned an empty response")  # provider error: never retried
        try:
            records = _read_records(raw, expected)
        except Exception as exc:
            return failed(f"the answer is not usable seed data: {exc}")  # parse error: never retried
        try:
            rejected = check_records(workspace_dir, structure, records)
        except Exception as exc:
            return failed(str(exc))
        attempts.append({"attempt": number, "approved": not rejected,
                         "reason": "every record builds and serialises" if not rejected else "; ".join(rejected)})
        if not rejected:
            path = os.path.join(workspace_dir, SEED_FILE)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(records, f, indent=2, ensure_ascii=False)
            print(f"[Compiler:Seed] Wrote {sum(len(v) for v in records.values())} sample records "
                  f"({', '.join(expected)}) in {round(time.time() - start, 2)}s", flush=True)
            return {"success": True, "files": [path], "attempts": attempts, "records": records,
                    "elapsed_seconds": round(time.time() - start, 2)}
        feedback = ("\n## The domain rejected the previous records\n" + "\n".join(f"- {r}" for r in rejected)
                    + "\nFix exactly these records and return the complete answer again.\n\n")
    return failed("the domain rejected the records twice: " + attempts[-1]["reason"])
