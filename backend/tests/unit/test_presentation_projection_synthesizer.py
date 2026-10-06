"""
Unit tests for Presentation Projection Synthesizer and Resilient Entrypoints.
Verifies fallback templates adhere to Viewport Containment and resilient module imports.
"""

import pytest
from onboarding.skeleton_builder import generate_frontend_main_tsx


def test_resilient_main_tsx_entrypoint_handles_any_export_pattern():
    """Verifies that main.tsx handles both default and named export without requiring monkey patches."""
    main_tsx = generate_frontend_main_tsx()
    assert "* as AppModule" in main_tsx
    assert "(AppModule as any).default || (AppModule as any).App" in main_tsx

