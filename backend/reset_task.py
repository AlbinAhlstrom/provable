import json

with open('/home/albin/projects/pme/src/requirements.json', 'r') as f:
    reqs = json.load(f)

for r in reqs:
    if r['id'] == 'REQ-1122':
        r['status'] = 'Backlog'
        r['feedback'] = None
        print(f"Reset {r['id']} to Backlog")

with open('/home/albin/projects/pme/src/requirements.json', 'w') as f:
    json.dump(reqs, f, indent=2)

print("Done")
