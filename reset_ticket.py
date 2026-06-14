import json

with open("/home/albin/projects/pme/src/requirements.json", "r") as f:
    reqs = json.load(f)

for req in reqs:
    if req["id"] == "REQ-756":
        req["status"] = "Backlog"

with open("/home/albin/projects/pme/src/requirements.json", "w") as f:
    json.dump(reqs, f, indent=2)
