import json
import subprocess

diff = subprocess.run(["git", "diff", "main", "ticket/REQ-756"], cwd="/home/albin/projects/pme/workspace", capture_output=True, text=True).stdout

with open("/home/albin/projects/pme/src/requirements.json", "r") as f:
    reqs = json.load(f)

for req in reqs:
    if req["id"] == "REQ-756":
        req["status"] = "Review"
        req["proposedCode"] = diff

with open("/home/albin/projects/pme/src/requirements.json", "w") as f:
    json.dump(reqs, f, indent=2)
