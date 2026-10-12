#!/usr/bin/env python3
"""Build and read the struggle corpus (see backend/struggle_corpus.py): where recorded runs got stuck, grouped.

Usage:
    python scripts/struggle_corpus.py              add the finished runs not yet counted, then list every kind of
                                                   struggle, the most frequent first
    python scripts/struggle_corpus.py --show ID    one entry in full: runs, models, examples and its review

A line reads "<times it happened> of <times the step ran>  <step>/<verdict>". `nearest_llm` is the LLM call that most
often came just before it in the call tree: the prompt to read first, not a verdict on which prompt is at fault.
Calls no model.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backend"))

import run_recorder  # noqa: E402
import struggle_corpus  # noqa: E402


def main():
    path = struggle_corpus.corpus_path()
    corpus = struggle_corpus.build(run_recorder.runs_root(), path)
    if "--show" in sys.argv:
        entry_id = (sys.argv[sys.argv.index("--show") + 1:] or [None])[0]
        if entry_id not in corpus["entries"]:
            sys.exit(f"No such entry: {entry_id}. Entries: {', '.join(sorted(corpus['entries']))}")
        print(json.dumps(corpus["entries"][entry_id], indent=2, ensure_ascii=True))
        return
    print("\n".join(struggle_corpus.report_lines(corpus)))
    print(f"\nCorpus: {path}")


if __name__ == "__main__":
    main()
