"""
A part that opens over the page and closes again: kept open and closed by generated code, so the page's writer
only says what is in it.

A menu, a list of choices or a panel of settings is opened by a control and has to close when a choice is made, when
Escape is pressed, or when a person presses somewhere else. The browser has no event for the last one. Asked to
write it, the page's writer closed a menu on a timer started when its opener lost focus: the press on an item took
the focus, and 150 ms later the item was gone. A test's click is over before that; a person's press is not, so a
choice from the menu was made about one time in three. So it is written once here (`OPENING_TS`, placed beside the
API clients as `src/api/opening.ts`): the part closes on a press that begins outside it, and on nothing that a press
inside it sets off.
"""

FILE_NAME = "opening.ts"

OPENING_TS = '''/** Generated: keeps a part that opens over the page (a menu, a list of choices, a panel) open and closed. */
import { useEffect, useRef, useState } from 'react';

/**
 * `open` says whether the part is shown. `toggle` is what its control does, `close` what a choice in it does.
 * `within` goes, as `ref`, on the element that holds both the control and what opens: a press that begins
 * outside that element closes the part, and so does Escape. A press inside it never does, however long it lasts.
 */
export function useOpening<T extends HTMLElement = HTMLDivElement>() {
  const [open, setOpen] = useState(false);
  const within = useRef<T>(null);

  useEffect(() => {
    if (!open) return;
    const pressed = (e: Event) => {
      if (within.current && !within.current.contains(e.target as Node)) setOpen(false);
    };
    const key = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setOpen(false);
    };
    document.addEventListener('pointerdown', pressed);
    document.addEventListener('keydown', key);
    return () => {
      document.removeEventListener('pointerdown', pressed);
      document.removeEventListener('keydown', key);
    };
  }, [open]);

  return { open, within, toggle: () => setOpen((now) => !now), close: () => setOpen(false) };
}
'''


def opening_block() -> str:
    """What the page's writer is told of the helper."""
    return (
        f"- `src/api/{FILE_NAME}` exports exactly `useOpening()`, a hook for a part that a control opens over the "
        "page and that closes again (a menu and its items, a list of choices, a panel of settings). It returns "
        "`{ open, toggle, close, within }`: `open` says whether the part is shown, `toggle` is what the control "
        "that opens it does, `close` is called after a choice in it is made, and `within` is the `ref` of the "
        "element that holds both the control and what opens "
        "(`const menu = useOpening(); <div ref={menu.within}><button onClick={menu.toggle}>...</button>"
        "{menu.open && <div>...</div>}</div>`). It closes the part when a person presses anywhere outside that "
        "element or presses Escape. Every such part is kept open and closed by one call of this hook, and by "
        "nothing else: it has no state, timer or focus handler of its own for that.")
