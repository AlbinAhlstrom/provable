import os
import ast
import re

backend_dir = r"c:\Users\ahlst\Documents\GitHub\provable\backend"

print("=" * 80)
print("EXHAUSTIVE AST SCAN: KEYWORD LISTS, HEURISTIC STRING BAGS & NAIVE CLASSIFIERS")
print("=" * 80)

findings = []

for root, dirs, files in os.walk(backend_dir):
    if "__pycache__" in root or ".pytest_cache" in root or "logs" in root or "tests" in root:
        continue
    for file in files:
        if not file.endswith(".py"):
            continue
        filepath = os.path.join(root, file)
        relpath = os.path.relpath(filepath, backend_dir)
        with open(filepath, "r", encoding="utf-8") as f:
            code = f.read()
        try:
            tree = ast.parse(code, filename=relpath)
        except Exception as e:
            print(f"Error parsing {relpath}: {e}")
            continue

        lines = code.splitlines()

        for node in ast.walk(tree):
            # Check for assignments of lists of strings (3+ string literals)
            if isinstance(node, ast.Assign):
                if isinstance(node.value, (ast.List, ast.Set, ast.Tuple)):
                    elts = node.value.elts
                    if len(elts) >= 3 and all(isinstance(e, ast.Constant) and isinstance(e.value, str) for e in elts):
                        targets = [ast.unparse(t) for t in node.targets]
                        str_vals = [e.value for e in elts]
                        findings.append({
                            "type": "STRING_LIST_ASSIGNMENT",
                            "file": relpath,
                            "line": node.lineno,
                            "target": ", ".join(targets),
                            "values": str_vals[:8],
                            "count": len(str_vals),
                            "code": lines[node.lineno-1].strip()
                        })

            # Check for dict constants with 'keywords' or lists of strings inside dicts
            if isinstance(node, ast.Dict):
                for k, v in zip(node.keys, node.values):
                    if isinstance(k, ast.Constant) and k.value in ["keywords", "synonyms", "triggers", "terms", "rules"]:
                        if isinstance(v, (ast.List, ast.Set, ast.Tuple)):
                            str_vals = [e.value for e in v.elts if isinstance(e, ast.Constant) and isinstance(e.value, str)]
                            findings.append({
                                "type": "DICT_KEYWORD_BAG",
                                "file": relpath,
                                "line": node.lineno,
                                "key": k.value,
                                "values": str_vals[:8],
                                "count": len(str_vals),
                                "code": lines[node.lineno-1].strip()
                            })

            # Check for list comprehension / any() / sum() testing string in string
            if isinstance(node, (ast.ListComp, ast.GeneratorExp)):
                # e.g. [k in text for k in ...] or sum(1 for kw in ... if kw in text)
                unparsed = ast.unparse(node)
                if " in " in unparsed and any(term in unparsed for term in ["pitch", "text", "lower", "name", "desc"]):
                    findings.append({
                        "type": "NAIVE_STRING_MATCHING_LOOP",
                        "file": relpath,
                        "line": node.lineno,
                        "code": lines[node.lineno-1].strip()
                    })

print(f"Total heuristic keyword / string-bag patterns found: {len(findings)}\n")

grouped = {}
for f in findings:
    grouped.setdefault(f["file"], []).append(f)

for filename, items in grouped.items():
    print(f"\nFILE: {filename} ({len(items)} instances)")
    for it in items:
        if it["type"] == "DICT_KEYWORD_BAG":
            print(f"  Line {it['line']:4d}: [DICT_KEYWORD_BAG] key='{it['key']}' ({it['count']} items): {it['values']}")
        elif it["type"] == "STRING_LIST_ASSIGNMENT":
            print(f"  Line {it['line']:4d}: [STRING_LIST_ASSIGNMENT] {it['target']} = {it['values']} (len={it['count']})")
        elif it["type"] == "NAIVE_STRING_MATCHING_LOOP":
            print(f"  Line {it['line']:4d}: [NAIVE_STRING_MATCHING_LOOP] {it['code']}")
