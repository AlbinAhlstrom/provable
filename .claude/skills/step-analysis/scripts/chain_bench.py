"""Runs the pitch expansion and the UX plan as a chain, each on a model of its own, and keeps both answers.

    python chain_bench.py --pitches <pitches.json> --out <dir> --tag <name> [--chains opus-opus,sonnet-haiku]
                          [--expansion <prompt.md>] [--plan <prompt.md>] [--effort low] [--repeat 1] [--reuse <tag>]

pitches.json: {"<case>": {"pitch": "<the pitch as a user types it>", "intent": {<a classified ProductIntent>}}, ...}
A chain is <expansion model>-<plan model>. Between the two the engine's own decomposition runs (on the model the
app is configured for), because the plan is given its entities and rules. --reuse takes the expansions and
decompositions of an earlier tag and runs only the plan, for a draft that changes the plan's prompt alone.

Written to <out>/<tag>/: <case>_<chain>[_n].expansion.md, .inputs.json (what filled the plan's prompt), .md (the
plan) and runs.json, in the shape `step_bench.py score` reads. Nothing else is touched.
"""
import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "backend"))
PROMPTS = os.path.join(REPO, "backend", "prompts")
MODELS = {"haiku": "claude-haiku-5-5", "sonnet": "claude-sonnet-5-5", "opus": "claude-opus-5-5"}

parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("--pitches", required=True)
parser.add_argument("--out", required=True)
parser.add_argument("--tag", required=True)
parser.add_argument("--chains", default="opus-opus,sonnet-haiku")
parser.add_argument("--expansion", default=os.path.join(PROMPTS, "prompt_expansion.md"))
parser.add_argument("--plan", default=os.path.join(PROMPTS, "ux_planning.md"))
parser.add_argument("--effort", default="low")
parser.add_argument("--repeat", type=int, default=1)
parser.add_argument("--reuse", default="", help="tag whose expansions and decompositions are used again")
args = parser.parse_args()

from dotenv import load_dotenv

load_dotenv(os.path.join(REPO, ".env"))
import llm_anthropic
from llm_cost import price_for, usd_to_sek
from onboarding.intent import ProductIntent, intent_block
from onboarding.router_engine import decompose_pitch_into_structure_and_inbox
from onboarding.ux_planner import plan_prompt_values

KEY = os.environ["CLAUDE_API_KEY"]
pitches = json.load(open(args.pitches, encoding="utf-8"))
folder = os.path.join(args.out, args.tag)
os.makedirs(folder, exist_ok=True)
templates = {step: open(path, encoding="utf-8-sig").read()
             for step, path in (("expansion", args.expansion), ("plan", args.plan))}
for step, text in templates.items():
    open(os.path.join(folder, f"prompt_{step}.md"), "w", encoding="utf-8").write(text)


def ask(short, prompt):
    """One call: the answer, the seconds it took and what it cost in SEK."""
    model = MODELS.get(short, short)
    started = time.time()
    text, usage, _ = llm_anthropic.complete(KEY, model, prompt, None, args.effort, None, 600.0)
    price = price_for(model)
    usd = (usage["prompt_tokens"] * price.input + usage["completion_tokens"] * price.output) / 1_000_000
    return text.strip(), round(time.time() - started, 1), round(usd * usd_to_sek(), 4)


def fill(template, values):
    for name, value in values.items():
        template = template.replace("{" + name + "}", value)
    return template


def one(job):
    case, chain, turn = job
    first, second = chain.split("-")
    name = f"{case}_{chain}" + (f"_{turn}" if args.repeat > 1 else "")
    path = os.path.join(folder, name)
    intent = ProductIntent.from_dict(pitches[case]["intent"])
    row = {"file": name + ".md", "case": case, "model": chain}
    if args.reuse:
        source = os.path.join(args.out, args.reuse, name)
        expansion = open(source + ".expansion.md", encoding="utf-8").read()
        values = json.load(open(source + ".inputs.json", encoding="utf-8"))
        row.update(expansion_seconds=0.0, expansion_sek=0.0)
    else:
        expansion, seconds, sek = ask(first, fill(templates["expansion"], {
            "business_pitch": pitches[case]["pitch"], "intent_block": intent_block(intent)}))
        row.update(expansion_seconds=seconds, expansion_sek=sek)
        result = decompose_pitch_into_structure_and_inbox(expansion, intent)
        master = result.structure.master_entity()
        values = plan_prompt_values(expansion, result.structure, None, getattr(master, "name", "") or "", intent,
                                    result.inbox.specs)
    open(path + ".expansion.md", "w", encoding="utf-8").write(expansion)
    json.dump(values, open(path + ".inputs.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    plan, seconds, sek = ask(second, fill(templates["plan"], values))
    open(path + ".md", "w", encoding="utf-8").write(plan)
    row.update(plan_seconds=seconds, plan_sek=sek, seconds=round(row["expansion_seconds"] + seconds, 1),
               sek=round(row["expansion_sek"] + sek, 4), words=len(plan.split()),
               expansion_words=len(expansion.split()))
    return row


jobs = [(case, chain, turn) for case in pitches for chain in args.chains.split(",")
        for turn in range(1, args.repeat + 1)]
with ThreadPoolExecutor(max_workers=4) as pool:
    rows = list(pool.map(one, jobs))
json.dump(rows, open(os.path.join(folder, "runs.json"), "w", encoding="utf-8"), indent=1)
for row in rows:
    print(row)
