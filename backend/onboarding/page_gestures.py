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
