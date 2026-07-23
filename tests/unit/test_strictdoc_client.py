import pytest
from integrations.strictdoc_client import _slugify_section_title, generate_sdoc_content, parse_sdoc


@pytest.mark.unit
def test_slugify_section_title():
    """Test section title slugification logic."""
    assert _slugify_section_title("Game Board UI") == "FOLDER-game-board-ui"
    assert _slugify_section_title("  Authentication & User Roles  ") == "FOLDER-authentication-user-roles"


@pytest.mark.unit
def test_generate_and_parse_sdoc(tmp_path):
    """Test serializing requirements to SDoc format and parsing them back."""
    reqs = [
        {
            "id": "REQ-001",
            "title": "User Authentication",
            "description": "User must be able to log in with password.",
            "type": "requirement",
            "priority": "P1",
            "status": "in_progress",
            "parent_id": None
        }
    ]

    sdoc_str = generate_sdoc_content(reqs)
    assert "[DOCUMENT]" in sdoc_str
    assert "TITLE: User Authentication" in sdoc_str
    assert "UID: REQ-001" in sdoc_str

    sdoc_file = tmp_path / "test.sdoc"
    sdoc_file.write_text(sdoc_str, encoding="utf-8")

    parsed = parse_sdoc(str(sdoc_file))
    assert len(parsed) >= 1
    found_req = next((r for r in parsed if r.get("id") == "REQ-001"), None)
    assert found_req is not None
    assert found_req["title"] == "User Authentication"
