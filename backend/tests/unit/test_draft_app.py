"""The app a visitor sees before its page is written reads as a first draft of that app (skeleton_builder,
onboarding/draft_theme.py).

The skeleton's stand-in used to be a dark admin tool: "<Entity> Management", a table of raw field names, an
"API Connected (:8001)" badge. Shown from the start of a build it looked like a different product. It now lists the
records the audience works with as cards under plain names, and takes its colours from the UX plan as soon as that
is decided, so the written page arrives as the same app filling in.
"""
from onboarding.draft_theme import DraftTheme, parse_draft_theme, theme_css, write_draft_theme
from onboarding.router_engine import AudienceRole, DomainStructureSchema, EntitySpec
from onboarding.skeleton_builder import generate_fullstack_skeleton_files

STRUCTURE = DomainStructureSchema(domain_name="Atelier Solene", entities=[
    EntitySpec(name="GuestReservation", audience_role=AudienceRole.CREATED,
               attributes=[{"name": "id", "type": "string"}, {"name": "guest_name", "type": "string"},
                           {"name": "salon_service_id", "type": "string"}]),
    EntitySpec(name="SalonService", audience_role=AudienceRole.SHOWN,
               attributes=[{"name": "id", "type": "string"}, {"name": "name", "type": "string"}, {"name": "price", "type": "float"}]),
    EntitySpec(name="AuditEntry", audience_role=AudienceRole.INTERNAL, attributes=[{"name": "id", "type": "string"}]),
])

DIRECTION = """- **Feel**: calm and warm.
- **Palette**: `bg-stone-50` page, white surface, `text-stone-900`, amber accent.
TOKENS background=#faf7f2 surface=#ffffff text=#1c1917 accent=#b45309 on_accent=#ffffff heading=serif
"""


def _file(files, *suffix):
    import os
    return next(code for path, code in files.items() if path.endswith(os.path.join(*suffix)) and "frontend" not in path)


def test_the_draft_names_things_the_way_a_visitor_would():
    """Verify the stand-in carries the app's name and plain record names, and nothing of an admin tool.

    id: TST-DRAFT-001
    Given: A structure with a created, a shown and an internal entity
    When: The skeleton's app and views are generated
    Then: The app shows its title and one tab per entity the audience works with, under plain plural names; the
          internal entity has no tab; no "Management" heading, API badge or table markup is left
    """
    files = generate_fullstack_skeleton_files(STRUCTURE, base_path="ws")
    app, view = _file(files, "src", "App.tsx"), _file(files, "src", "views", "SalonServiceView.tsx")

    assert "Atelier Solene" in app
    assert "Guest reservations" in app and "Salon services" in app and "Audit entries" not in app
    for leftover in ("Management", "API Connected", "8001", "domain aggregates", "<table"):
        assert leftover not in app and leftover not in view, leftover
    assert "Salon services" in view


def test_the_draft_shows_records_as_cards_and_leaves_ids_out():
    """Verify a record is presented by what it says, not by its keys.

    id: TST-DRAFT-002
    Given: An entity with an id, a name, a price and a reference to another record
    When: Its view is generated
    Then: The first descriptive field is the card's title, ids and references are not listed, and the view asks
          again while it has nothing to show (the starting content is written a little after the app starts)
    """
    files = generate_fullstack_skeleton_files(STRUCTURE, base_path="ws")
    service, reservation = _file(files, "src", "views", "SalonServiceView.tsx"), _file(files, "src", "views", "GuestReservationView.tsx")

    assert "const TITLE_FIELD = 'name';" in service and "const TITLE_FIELD = 'guest_name';" in reservation
    assert "endsWith('_id')" in service
    assert "setInterval" in service and "items.length" in service


def test_the_draft_takes_its_colours_from_the_theme_file():
    """Verify the stand-in is coloured by variables the build can change, with neutral values until it does.

    id: TST-DRAFT-003
    Given: A generated skeleton
    When: Its entry file, theme file and views are read
    Then: The entry imports the theme, the theme defines every draft variable, and the views use them
    """
    files = generate_fullstack_skeleton_files(STRUCTURE, base_path="ws")
    theme, view = _file(files, "src", "theme.css"), _file(files, "src", "views", "SalonServiceView.tsx")

    assert "import './theme.css';" in _file(files, "src", "main.tsx")
    for variable in ("--draft-bg", "--draft-surface", "--draft-text", "--draft-accent", "--draft-on-accent", "--draft-heading-font"):
        assert variable in theme
    assert "var(--draft-surface)" in view and "var(--draft-accent)" in view
    assert theme == theme_css(DraftTheme())


def test_the_ux_plans_tokens_become_the_theme():
    """Verify the palette the UX plan decided is read as typed values.

    id: TST-DRAFT-004
    Given: A visual direction that ends with its token line
    When: The direction is parsed
    Then: The theme holds the five colours and the heading family, and its CSS carries them
    """
    theme = parse_draft_theme(DIRECTION)
    assert theme == DraftTheme(background="#faf7f2", surface="#ffffff", text="#1c1917", accent="#b45309",
                               on_accent="#ffffff", heading="serif")
    css = theme_css(theme)
    assert "--draft-bg: #faf7f2;" in css and "--draft-accent: #b45309;" in css and "serif" in css


def test_a_direction_without_complete_tokens_gives_no_theme():
    """Verify an incomplete token line is not half-applied.

    id: TST-DRAFT-005
    Given: A direction with no token line, and one whose line lacks the accent
    When: Each is parsed
    Then: Neither gives a theme
    """
    assert parse_draft_theme("- **Feel**: calm.") is None
    assert parse_draft_theme("TOKENS background=#faf7f2 surface=#ffffff text=#1c1917 on_accent=#ffffff heading=serif") is None


def test_the_theme_is_written_where_the_app_is_served_from(tmp_path):
    """Verify writing the theme replaces the neutral one of the skeleton and reports the file.

    id: TST-DRAFT-006
    Given: A workspace with a skeleton's theme file
    When: The UX plan's theme is written
    Then: The served theme file holds the plan's colours, and its workspace-relative path is returned
    """
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "theme.css").write_text(theme_css(DraftTheme()), encoding="utf-8")
    written = write_draft_theme(str(tmp_path), parse_draft_theme(DIRECTION))
    assert written == ["src/theme.css"]
    assert "--draft-bg: #faf7f2;" in (tmp_path / "src" / "theme.css").read_text(encoding="utf-8")
