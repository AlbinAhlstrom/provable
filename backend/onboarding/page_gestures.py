"""
The gestures of a part: recognised by generated code, so the page's writer only says what each one does.

A plan gives an action its gestures, for a mouse and for a finger (a click or a tap, a right click or a long press,
two buttons at once or a double click). The browser has an event for some of them and none for a long press or for
two buttons held together: those are made of presses and releases, and the click and the menu that end them have to
be left unanswered. Asked to write that, the page's writer wrote the gestures that have an event and left the others
out. So it is written once here (`GESTURES_TS`, placed beside the API clients as `src/api/gestures.ts`), and the
page spreads its result on a part.

What the helper keeps between events is kept for the whole page, not per part: a person has one pointer, and the
release that ends a gesture can land on another part than the press that began it.
"""

FILE_NAME = "gestures.ts"
LONG_PRESS_MS = 500

GESTURES_TS = f'''/** Generated: recognises the gestures of a part, for a mouse and for a finger. Spread the result on the element. */

export interface Gestures {{
  /** A left click or a tap. */
  click?: () => void;
  /** A right click, or a finger held down for half a second. */
  secondary?: () => void;
  /** A double click or a double tap. */
  double?: () => void;
  /** The left and the right button held down together. */
  both?: () => void;
  /** Told true when a press on the part begins and false when it ends, for a look that lasts while it is held. */
  press?: (down: boolean) => void;
}}

type Press = {{ buttons: number; preventDefault: () => void }};

// One pointer for the whole page: what a gesture leaves unanswered may arrive on another part than it began on
let together = false;                          // both buttons went down; the click and the menu of their releases are not answered
let held = false;                              // a long press was answered; the tap and the menu that end it are not
let waiting: ReturnType<typeof setTimeout> | null = null;

function stopWaiting(): void {{
  if (waiting !== null) clearTimeout(waiting);
  waiting = null;
}}

export function gestures(on: Gestures) {{
  return {{
    onMouseDown: (e: Press) => {{
      held = false;
      together = e.buttons === 3;
      on.press?.(true);
      if (together && on.both) {{
        e.preventDefault();
        on.both();
      }}
    }},
    onMouseUp: (_e: Press) => on.press?.(false),
    onMouseLeave: (_e: Press) => on.press?.(false),
    onClick: (_e: Press) => {{
      if (together || held) return;
      on.click?.();
    }},
    onDoubleClick: (_e: Press) => {{
      if (together || held) return;
      on.double?.();
    }},
    onContextMenu: (e: Press) => {{
      e.preventDefault();
      stopWaiting();
      if (together || held) return;
      on.secondary?.();
    }},
    onTouchStart: (_e: unknown) => {{
      held = false;
      together = false;
      stopWaiting();
      on.press?.(true);
      if (!on.secondary) return;
      waiting = setTimeout(() => {{
        waiting = null;
        held = true;
        on.secondary?.();
      }}, {LONG_PRESS_MS});
    }},
    onTouchMove: (_e: unknown) => stopWaiting(),
    onTouchEnd: (_e: unknown) => {{
      stopWaiting();
      on.press?.(false);
    }},
    onTouchCancel: (_e: unknown) => {{
      stopWaiting();
      on.press?.(false);
    }},
  }};
}}
'''


# How a page test does each gesture: exactly the events `GESTURES_TS` answers, written beside the parts a test finds
# (`tests/e2e/gestures.py`). A test's writer left to do it chose its own: a middle click for "both buttons", which
# nothing on the page answers.
TEST_FILE = "gestures.py"

GESTURES_PY = '''"""How a page test does a gesture to a part: exactly what the page's gesture helper (src/api/gestures.ts) answers.

Written by the engine (onboarding/page_gestures.py); a change made here is overwritten.
`part` is a locator, as `parts` returns it.
"""


def _centre(part):
    part.scroll_into_view_if_needed()
    box = part.bounding_box()
    part.page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
    return part.page.mouse


def click(part):
    """A left click, or a tap."""
    part.click()


def right_click(part):
    """A right click, or a finger held down."""
    part.click(button="right")


def double_click(part):
    """A double click, or a double tap."""
    part.dblclick()


def both_buttons(part):
    """The left and the right button pressed together on the part, then let go."""
    mouse = _centre(part)
    mouse.down(button="left")
    mouse.down(button="right")
    mouse.up(button="right")
    mouse.up(button="left")


def press(part):
    """A press on the part, held until `release`: for what the page shows while a part is held down."""
    _centre(part).down(button="left")


def release(part):
    """Lets go of the press `press` began; where it ends over the part, that is a click as well."""
    part.page.mouse.up(button="left")
'''


def gestures_test_block() -> str:
    """What a page test's writer is told of the steps."""
    return (
        "## Gestures\n`import gestures` does a gesture to a part the way the page answers it, `part` being a locator "
        "from `parts`: `gestures.click(part)` (a click or a tap), `gestures.right_click(part)` (a right click or a "
        "long press), `gestures.double_click(part)` (a double click or a double tap), `gestures.both_buttons(part)` "
        "(the left and the right button together), and `gestures.press(part)` with `gestures.release(part)` around "
        "what the page shows while a part is held down. Do every gesture of the rule's When through these steps. A "
        "gesture that is not among them (a middle click, a click with a key held) is answered by nothing on the page: "
        "where the rule names one, use the step it stands beside in the plan's gestures.\n")


def gestures_block() -> str:
    """What the page's writer is told of the helper."""
    return (
        f"- `src/api/{FILE_NAME}` exports exactly `gestures(on)`, where `on` is "
        "`{ click?, secondary?, double?, both?, press? }`: `click` for a left click or a tap, `secondary` for a right "
        "click or a long press, `double` for a double click or a double tap, `both` for the left and right buttons "
        "held together, each a function without arguments, and `press(down: boolean)`, told when a press on the part "
        "begins and ends (for a look that lasts while it is held). It returns the event handlers of an element, to "
        "be spread on it (`<div {...gestures({ click: () => ..., secondary: () => ... })} />`), and keeps the browser's own menu from "
        "opening there. A part whose action the blueprint gives a right click, a long press, a double click or two "
        "buttons gets all its handlers from this one call, with every gesture the blueprint names for it, and has no "
        "mouse or touch handler of its own beside it.")
