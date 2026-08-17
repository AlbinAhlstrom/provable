"""
Automated Multi-Domain Synthesis & Light-Theme Benchmark Test Suite.

Verifies that the Provable synthesis pipeline generates valid, syntax-clean TSX applications
with correct light-theme design system token binding across 5 distinct domain pitches.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from onboarding.frontend_planning_engine import (
    run_frontend_planning_pipeline,
    assemble_app_tsx_from_blueprint
)
from onboarding.code_verifier import verify_tsx_syntax


DOMAIN_TEST_PITCHES = [
    {
        "domain": "Babysitter Care",
        "pitch": "A site for parents to book a babysitter. The booking process should go through selecting sitters and open weekly calendar hours.",
        "expected_category": "service_booking",
        "expected_archetype": "warm_lifestyle_light"
    },
    {
        "domain": "Artisan Bakery",
        "pitch": "A boutique sourdough bakery for pre-ordering artisan bread and pastries with cart checkout.",
        "expected_category": "e_commerce",
        "expected_archetype": "modern_fresh_light"
    },
    {
        "domain": "Wash & Fold Laundry",
        "pitch": "A pickup and delivery wash-and-fold laundry service with scheduling time slots.",
        "expected_category": "service_booking",
        "expected_archetype": "warm_lifestyle_light"
    },
    {
        "domain": "Luxury Car Rental",
        "pitch": "A sports car rental booking portal to select vehicles and rental dates.",
        "expected_category": "service_booking",
        "expected_archetype": "warm_lifestyle_light"
    },
    {
        "domain": "Student Tutoring",
        "pitch": "A site for students to book a tutor. The booking process should go through selecting tutors and open weekly calendar hours.",
        "expected_category": "service_booking",
        "expected_archetype": "warm_lifestyle_light"
    },
    {
        "domain": "Kitchen Operations KDS",
        "pitch": "A restaurant kitchen order display board for line cooks and kitchen managers.",
        "expected_category": "operations_dashboard",
        "expected_archetype": "clean_b2b_light"
    }
]


@pytest.mark.parametrize("case", DOMAIN_TEST_PITCHES, ids=[c["domain"] for c in DOMAIN_TEST_PITCHES])
def test_multi_domain_synthesis_pipeline(case):
    pitch = case["pitch"]
    
    # 1. Execute Multi-Agent Planning Pipeline
    blueprint = run_frontend_planning_pipeline(pitch)
    assert blueprint is not None
    assert blueprint.business_pitch == pitch
    assert blueprint.category_layout.category_id == case["expected_category"]
    assert blueprint.aesthetics.archetype == case["expected_archetype"]

    # 2. Assemble React TSX Code
    tsx_code = assemble_app_tsx_from_blueprint(blueprint)
    assert tsx_code is not None
    assert "export default function App" in tsx_code or "export default App" in tsx_code or "function App" in tsx_code

    # 3. AST Syntax Verification Gate
    is_valid, err_msg = verify_tsx_syntax(tsx_code)
    assert is_valid, f"TSX syntax error for {case['domain']}: {err_msg}"

    # 4. Light Theme Token Binding Verification
    # Ensure standard CSS variable tokens are injected
    assert "--bg-main:" in tsx_code or "var(--bg-main)" in tsx_code
    
    # For non-dev-tools, verify no hardcoded dark slate #0f172a background remains
    if case["expected_archetype"] != "dark_developer_terminal":
        assert "background: '#0f172a'" not in tsx_code, f"Hardcoded dark slate background leaked in {case['domain']}"
        assert "background: '#1e293b'" not in tsx_code, f"Hardcoded dark card background leaked in {case['domain']}"


def test_tutoring_domain_vocabulary_isolation():
    pitch = "A site for students to book a tutor for math and science."
    blueprint = run_frontend_planning_pipeline(pitch)
    tsx_code = assemble_app_tsx_from_blueprint(blueprint)

    # Verify zero babysitter / Nestly / sitter vocabulary leakage
    code_lower = tsx_code.lower()
    assert "sitter" not in code_lower, "Babysitter vocabulary 'sitter' leaked into tutoring app!"
    assert "babysitter" not in code_lower, "Babysitter vocabulary 'babysitter' leaked into tutoring app!"
    assert "nestly" not in code_lower, "Nestly brand title leaked into tutoring app!"
    assert "tutor" in code_lower, "Tutoring domain noun 'tutor' missing from generated UI!"
    assert blueprint.aesthetics.domain_display_title == "EduBook"


if __name__ == "__main__":
    pytest.main(["-v", __file__])
