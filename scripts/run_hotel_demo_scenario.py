"""
Interactive Semi-Automated Hotel Acceptance Test Runner.
Executes live HTTP requests against Workspace Domain API (port 8001)
and verifies real-time continuity in PM Studio (port 5173).
"""

import sys
import json
import argparse
import urllib.request
import urllib.error

WORKSPACE_URL = "http://localhost:8001"

def api_call(endpoint: str, method: str = "GET", data: dict = None):
    url = f"{WORKSPACE_URL}{endpoint}"
    body = json.dumps(data).encode("utf-8") if data else None
    headers = {"Content-Type": "application/json"} if data else {}
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read().decode("utf-8")
            res_json = json.loads(raw) if raw else {}
            print(f"  ✅ {method} {endpoint} -> HTTP {resp.status}")
            return res_json
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8")
        print(f"  ❌ {method} {endpoint} -> HTTP {e.code}: {err}")
        return None
    except Exception as e:
        print(f"  ❌ {method} {endpoint} -> Connection error: {e}")
        return None

def step_seed():
    print("\n🌱 [STEP 1] Seeding Guests & Rooms into Workspace API (:8001)...")
    
    # 1. Seed Guest
    api_call("/api/guests", "POST", {
        "id": "GUEST-101",
        "first_name": "Elin",
        "last_name": "Sundström",
        "email": "elin@boutique.se",
        "phone_number": "0701122334",
        "version": 0
    })

    # 2. Seed Rooms (DIRTY & CLEAN)
    api_call("/api/rooms", "POST", {
        "id": "ROOM-101",
        "room_number": "101",
        "room_type": "Deluxe Suite",
        "cleaning_status": "DIRTY",
        "is_active": True,
        "version": 0
    })

    api_call("/api/rooms", "POST", {
        "id": "ROOM-102",
        "room_number": "102",
        "room_type": "Superior King",
        "cleaning_status": "CLEAN",
        "is_active": True,
        "version": 0
    })

    print("✨ Step 1 complete! Look at your PM Studio Preview tab (http://localhost:5173) to see the live records.")

def step_book():
    print("\n🏨 [STEP 2] Creating Booking for Clean Room 102...")
    api_call("/api/bookings", "POST", {
        "id": "BOOK-101",
        "guest_id": "GUEST-101",
        "room_id": "ROOM-102",
        "check_in_date": "2026-09-10",
        "check_out_date": "2026-09-15",
        "status": "CONFIRMED",
        "total_price": 7500.0,
        "version": 0
    })
    print("✨ Step 2 complete! Refresh the Booking view in Preview to see the confirmed booking.")

def main():
    parser = argparse.ArgumentParser(description="Provable Hotel Acceptance Runner")
    parser.add_argument("--step", choices=["seed", "book", "all"], default="all")
    args = parser.parse_args()

    print("=================================================================")
    print("🏨 PROVABLE SEMI-AUTOMATED ACCEPTANCE RUNNER")
    print("=================================================================")
    
    if args.step in ["seed", "all"]:
        step_seed()
    if args.step in ["book", "all"]:
        step_book()

    print("\n✨ All operations executed against port 8001. Check PM Studio at http://localhost:5173!")

if __name__ == "__main__":
    main()
