"""Runs one pipeline step alone on several models, and scores what they wrote.

    python step_bench.py run   --template <prompt.md> --cases <cases.json> --out <dir> --tag <name>
                               [--models haiku,sonnet,opus] [--effort low] [--repeat 1] [--json]
    python step_bench.py score --checklist <checklist.json> --out <dir> <tag> [<tag> ...]

cases.json:     {"<case>": {"<placeholder>": "<value>", ...}, ...}   one case per pitch; a value fills {placeholder}
checklist.json: {"<case>": {"wanted": {"<item>": "<regex>"}, "unwanted": {"<item>": "<regex>"}}, ...}

It calls the provider directly and writes only under --out, so the app, its workspace and its database are untouched.
"""
import argparse
import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "backend"))

MODELS = {"haiku": "claude-haiku-5-5", "sonnet": "claude-sonnet-5-5", "opus": "claude-opus-5-5"}


def render(template, values):
    for name, value in values.items():
        template = template.replace("{" + name + "}", value)
    return template


def run(args):
    from dotenv import load_dotenv
    load_dotenv(os.path.join(REPO, ".env"))
    import llm_anthropic
    from llm_cost import price_for, usd_to_sek

    key = os.environ["CLAUDE_API_KEY"]
    template = open(args.template, encoding="utf-8-sig").read()
    cases = json.load(open(args.cases, encoding="utf-8"))
    folder = os.path.join(args.out, args.tag)
    os.makedirs(folder, exist_ok=True)

    def one(job):
        case, short, turn = job
        model = MODELS.get(short, short)
        prompt = render(template, cases[case])
        started = time.time()
        text, usage, stop = llm_anthropic.complete(key, model, prompt, None, args.effort,
                                                   {"type": "object"} if args.json else None, 600.0)
        seconds = time.time() - started
        price = price_for(model)
        usd = (usage["prompt_tokens"] * price.input + usage["completion_tokens"] * price.output) / 1_000_000
        name = f"{case}_{short}" + (f"_{turn}" if args.repeat > 1 else "")
        open(os.path.join(folder, name + ".md"), "w", encoding="utf-8").write(text)
        return {"file": name + ".md", "case": case, "model": short, "seconds": round(seconds, 1),
                "in": usage["prompt_tokens"], "out": usage["completion_tokens"],
                "sek": round(usd * usd_to_sek(), 4), "words": len(text.split()), "stop": stop}

    jobs = [(case, short, turn) for case in cases for short in args.models.split(",")
            for turn in range(1, args.repeat + 1)]
    with ThreadPoolExecutor(max_workers=3) as pool:
        rows = list(pool.map(one, jobs))
    json.dump(rows, open(os.path.join(folder, "runs.json"), "w", encoding="utf-8"), indent=1)
    for row in rows:
        print(row)


def score(args):
    checklist = json.load(open(args.checklist, encoding="utf-8"))
    for tag in args.tags:
        folder = os.path.join(args.out, tag)
        rows = json.load(open(os.path.join(folder, "runs.json"), encoding="utf-8"))
        print(f"== {tag}")
        totals = {}
        for row in rows:
            text = open(os.path.join(folder, row["file"]), encoding="utf-8").read().lower()
            checks = checklist.get(row["case"], {})
            wanted, unwanted = checks.get("wanted", {}), checks.get("unwanted", {})
            missing = [item for item, pattern in wanted.items() if not re.search(pattern, text, re.S)]
            present = [item for item, pattern in unwanted.items() if re.search(pattern, text, re.S)]
            total = totals.setdefault(row["model"], {"wanted": 0, "hit": 0, "unwanted": 0, "seconds": 0.0,
                                                     "sek": 0.0, "words": 0, "calls": 0})
            total["wanted"] += len(wanted)
            total["hit"] += len(wanted) - len(missing)
            total["unwanted"] += len(present)
            for field in ("seconds", "sek", "words"):
                total[field] += row[field]
            total["calls"] += 1
            print(f"  {row['file']}: {len(wanted) - len(missing)}/{len(wanted)} wanted, {len(present)} unwanted"
                  f" | missing: {missing} | unwanted: {present}")
        for model, total in totals.items():
            calls = total["calls"]
            print(f"  {model}: wanted {total['hit']}/{total['wanted']}, unwanted {total['unwanted']}, "
                  f"{total['seconds'] / calls:.1f} s, {total['sek'] / calls:.3f} SEK, "
                  f"{total['words'] // calls} words (average of {calls} calls)")


parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
commands = parser.add_subparsers(dest="command", required=True)
run_parser = commands.add_parser("run")
run_parser.add_argument("--template", required=True)
run_parser.add_argument("--cases", required=True)
run_parser.add_argument("--out", required=True)
run_parser.add_argument("--tag", required=True)
run_parser.add_argument("--models", default="haiku,sonnet,opus")
run_parser.add_argument("--effort", default="low")
run_parser.add_argument("--repeat", type=int, default=1)
run_parser.add_argument("--json", action="store_true", help="the step answers in JSON")
run_parser.set_defaults(handler=run)
score_parser = commands.add_parser("score")
score_parser.add_argument("--checklist", required=True)
score_parser.add_argument("--out", required=True)
score_parser.add_argument("tags", nargs="+")
score_parser.set_defaults(handler=score)
arguments = parser.parse_args()
arguments.handler(arguments)
