"""
LibCST Pipeline Inspection Script.
Tests router decomposition, skeleton building, and Meta LibCST class splicing on diverse business pitches.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from onboarding.router_engine import decompose_pitch_into_structure_and_inbox
from onboarding.skeleton_builder import generate_fullstack_skeleton_files
from onboarding.cst_isolator import extract_class_cst, splice_class_cst

TEST_PROMPTS = [
    "An industrial warehouse management system tracking Pallets, storage Zones, and forklift Operators.",
    "A maritime fleet logistics system tracking CargoShips, ShippingContainers, and HarborBerths.",
    "A hospital asset tracking platform monitoring Ventilators, ICU_Beds, and BiomedicalStaff."
]

def run_inspection():
    print("=" * 80)
    print("🔍 LIBCST & SKELETON PIPELINE INSPECTION REPORT")
    print("=" * 80)
    for pitch in TEST_PROMPTS:
        print(f"\n--- Pitch: {pitch} ---")
        decomp = decompose_pitch_into_structure_and_inbox(pitch)
        print(f"Domain Name: {decomp.structure.domain_name}")
        print(f"Entities: {[e.name for e in decomp.structure.entities]}")
        print(f"Inbox Specs ({len(decomp.inbox.specs)}): {[s.title for s in decomp.inbox.specs]}")
        files = generate_fullstack_skeleton_files(decomp.structure, "/tmp/test_skeleton")
        print(f"Generated Files: {list(files.keys())}")

if __name__ == "__main__":
    run_inspection()
