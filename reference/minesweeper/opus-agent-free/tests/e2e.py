"""Plays the game in headless Chrome: mouse, keyboard, touch, reload.

    python tests/e2e.py                 (opens index.html straight from disk)
    BASE_URL=http://localhost:5182/ python tests/e2e.py     (bash)
    $env:BASE_URL="http://localhost:5182/"; python tests/e2e.py   (PowerShell)

Needs Chrome and: pip install selenium
Screenshots land in tests/screenshots/.
"""
import os
import pathlib
import sys
import time

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.mouse_button import MouseButton
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = os.environ.get("BASE_URL") or (ROOT / "index.html").as_uri()
SHOTS = ROOT / "tests" / "screenshots"
SHOTS.mkdir(exist_ok=True)

results = []
problems = []  # browser console errors and failed requests


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    line = ("  ok   " if ok else "  FAIL ") + name + (f"  [{detail}]" if detail and not ok else "")
    print(line.encode("ascii", "replace").decode())


def url(query=""):
    return BASE + (("?" + query) if query else "")


GAME = "window.__minesweeper.game"
NUMBER_WITH_HIDDEN_SAFE_NEIGHBOUR = f"""(() => {{ const g = {GAME}, E = MinesweeperEngine;
    for (let i = 0; i < g.state.length; i++) {{
      if (g.state[i] !== 1 || !g.adj[i]) continue;
      if (E.neighbours(g, i).some(j => g.state[j] === 0 && !g.mine[j])) return i;
    }} return -1; }})()"""
BOARD_SNAPSHOT = "[...document.querySelectorAll('#board .cell')].map(b => b.className + '|' + b.textContent.trim()).join(',')"
WRAP_FITS = "document.getElementById('board-wrap').scrollWidth <= document.getElementById('board-wrap').clientWidth"
NO_PAGE_HSCROLL = "document.documentElement.scrollWidth <= window.innerWidth"


class Page:
    """Small wrapper so the test reads as what a player does."""

    def __init__(self, width, height, mobile=False, scheme="light"):
        opts = webdriver.ChromeOptions()
        opts.add_argument("--headless=new")
        opts.add_argument("--hide-scrollbars")
        opts.add_argument(f"--window-size={width},{height}")
        opts.set_capability("goog:loggingPrefs", {"browser": "ALL"})
        if mobile:
            opts.add_experimental_option("mobileEmulation", {
                "deviceMetrics": {"width": width, "height": height, "pixelRatio": 2, "touch": True, "mobile": True},
                "userAgent": "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) "
                             "Chrome/126.0.0.0 Mobile Safari/537.36",
            })
        self.d = webdriver.Chrome(options=opts)
        if not mobile:
            self.d.execute_cdp_cmd("Emulation.setDeviceMetricsOverride",
                                   {"width": width, "height": height, "deviceScaleFactor": 1, "mobile": False})
        # Headless Chrome inherits the operating system's colour scheme, so pin it.
        self.d.execute_cdp_cmd("Emulation.setEmulatedMedia",
                               {"features": [{"name": "prefers-color-scheme", "value": scheme}]})

    # --- plumbing ---
    def goto(self, target):
        self.d.get(target)

    def reload(self):
        self.collect_logs()
        self.d.refresh()

    def ev(self, expr):
        return self.d.execute_script("return (" + expr + ");")

    def g(self, expr):
        """Evaluate an expression with `g` bound to the live game object."""
        return self.ev(f"(() => {{ const g = {GAME}; return {expr}; }})()")

    def wait(self, ms):
        time.sleep(ms / 1000)

    def shot(self, name):
        self.d.save_screenshot(str(SHOTS / name))

    def collect_logs(self):
        for entry in self.d.get_log("browser"):
            if entry["level"] in ("SEVERE", "WARNING"):
                problems.append(f"{entry['level']}: {entry['message']}")

    def close(self):
        self.collect_logs()
        self.d.quit()

    # --- reading the page ---
    def el(self, sel):
        return self.d.find_element(By.CSS_SELECTOR, sel)

    def cell(self, i):
        return self.d.find_element(By.CSS_SELECTOR, f'#board .cell[data-i="{i}"]')

    def classes(self, i):
        return (self.cell(i).get_attribute("class") or "").split()

    def text(self, sel):
        return self.ev(f"document.querySelector({sel!r}).textContent.trim()")

    def count(self, sel):
        return self.ev(f"document.querySelectorAll({sel!r}).length")

    def pressed(self, sel):
        return self.el(sel).get_attribute("aria-pressed") == "true"

    def safe_hidden(self):
        return self.g("Array.from(g.state).map((s, i) => s === 0 && !g.mine[i] ? i : -1).filter(i => i >= 0)")

    def mines(self):
        return self.g("Array.from(g.mine).map((m, i) => m ? i : -1).filter(i => i >= 0)")

    def neighbours(self, i):
        return self.ev(f"MinesweeperEngine.neighbours({GAME}, {i})")

    # --- acting like a player ---
    def click(self, target):
        (self.cell(target) if isinstance(target, int) else self.el(target)).click()

    def right_click(self, i):
        ActionChains(self.d).context_click(self.cell(i)).perform()

    def middle_click(self, i):
        chain = ActionChains(self.d)
        chain.w3c_actions.pointer_action.move_to(self.cell(i))
        chain.w3c_actions.pointer_action.pointer_down(MouseButton.MIDDLE)
        chain.w3c_actions.pointer_action.pointer_up(MouseButton.MIDDLE)
        chain.perform()

    def key(self, key):
        ActionChains(self.d).send_keys(key).perform()

    def focus(self, i):
        self.ev(f"document.querySelector('#board .cell[data-i=\"{i}\"]').focus()")

    def active_index(self):
        return self.ev("document.activeElement.dataset.i")

    def fill(self, sel, value):
        box = self.el(sel)
        box.clear()
        box.send_keys(value)

    def _centre(self, target):
        sel = f'#board .cell[data-i="{target}"]' if isinstance(target, int) else target
        r = self.ev(f"(() => {{ const e = document.querySelector({sel!r}); e.scrollIntoView({{block: 'center', inline: 'center'}});"
                    " const r = e.getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; })()")
        return {"x": r[0], "y": r[1]}

    def touch(self, target, hold_ms=40):
        """A real touch sequence through the browser's input pipeline (not a synthetic DOM event)."""
        point = self._centre(target)
        self.d.execute_cdp_cmd("Input.dispatchTouchEvent", {"type": "touchStart", "touchPoints": [point]})
        self.wait(hold_ms)
        self.d.execute_cdp_cmd("Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": []})
        self.wait(120)

    def tap(self, target):
        self.touch(target)

    def long_press(self, target):
        self.touch(target, hold_ms=650)


def desktop_run():
    print("desktop: mouse and keyboard")
    page = Page(1280, 900)
    page.goto(url("seed=7"))

    # --- fresh board ---
    check("fresh: 81 cells", page.count("#board .cell") == 81)
    check("fresh: counter 010", page.text("#mines-left") == "010", page.text("#mines-left"))
    check("fresh: timer 000", page.text("#timer") == "000")
    check("fresh: status tells how to start", "first dig" in page.text("#status").lower(), page.text("#status"))
    check("fresh: Beginner is the pressed level", page.pressed('[data-level="beginner"]'))
    check("fresh: no mines placed yet (R2)", page.g("g.mine.reduce((a, b) => a + b, 0)") == 0)
    label = page.cell(0).get_attribute("aria-label")
    check("fresh: cells are labelled for screen readers (R20)", label == "Row 1, column 1: hidden", label)
    page.shot("01-fresh.png")

    # --- first click ---
    page.click(40)
    check("first click: game is playing", page.g("g.status") == "playing")
    check("first click: opened an area (R2)", page.count("#board .cell.open") >= 9, str(page.count("#board .cell.open")))
    check("first click: 10 mines placed (R3)", len(page.mines()) == 10)
    left = page.g("g.cols * g.rows - g.mines - g.revealedCount")
    check("first click: status line counts the safe squares left", page.text("#status") == f"{left} safe squares to go",
          page.text("#status"))
    page.wait(1300)
    check("timer runs after first click (R11)", int(page.text("#timer")) >= 1, page.text("#timer"))
    shown_ok = page.ev(f"""(() => {{ const g = {GAME};
        return [...document.querySelectorAll('#board .cell.open')].every(b => {{
          const i = +b.dataset.i; return b.textContent.trim() === (g.adj[i] ? String(g.adj[i]) : ''); }}); }})()""")
    check("revealed cells show the right numbers (R4)", shown_ok)
    label = page.ev("document.querySelector('#board .cell.open.n1').getAttribute('aria-label')")
    check("a revealed number is announced", label.endswith(": 1 mine nearby"), label)

    # --- flags ---
    m = page.mines()
    page.right_click(m[0])
    check("right-click plants a flag (R6)", "flagged" in page.classes(m[0]))
    check("counter drops to 009 (R10)", page.text("#mines-left") == "009", page.text("#mines-left"))
    page.click(m[0])
    check("left-click on a flag does nothing (R6)", page.g("g.status") == "playing" and "flagged" in page.classes(m[0]))
    page.right_click(m[0])
    check("right-click again removes the flag", "flagged" not in page.classes(m[0]) and page.text("#mines-left") == "010")
    menu_blocked = page.ev("""(() => { const e = new MouseEvent('contextmenu', {bubbles: true, cancelable: true});
        document.querySelector('#board .cell.open').dispatchEvent(e); return e.defaultPrevented; })()""")
    check("browser context menu is suppressed on the board", menu_blocked)

    # --- chord ---
    target = page.ev(NUMBER_WITH_HIDDEN_SAFE_NEIGHBOUR)
    check("found a number to chord on", target >= 0)
    if target >= 0:
        nb = page.neighbours(target)
        before = page.g("g.revealedCount")
        page.click(target)
        check("chord without enough flags does nothing (R7)", page.g("g.revealedCount") == before)
        for j in nb:
            if j in m:
                page.right_click(j)
        page.click(target)
        check("chord opens the other neighbours (R7)",
              all(page.g(f"g.state[{j}]") != 0 for j in nb) and page.g("g.status") != "lost")
    page.shot("02-midgame.png")

    # --- keyboard ---
    hidden = page.safe_hidden()
    check("still safe cells left to test the keyboard on", bool(hidden))
    if hidden:
        k = hidden[0]
        page.focus(k)
        page.key("f")
        check("F flags the focused cell (R16)", "flagged" in page.classes(k))
        page.key("f")
        check("F again removes it", "flagged" not in page.classes(k))
        page.key(Keys.ENTER)
        check("Enter digs the focused cell (R16)", page.g(f"g.state[{k}]") == 1)
    page.focus(0)
    page.key(Keys.ARROW_RIGHT)
    page.key(Keys.ARROW_DOWN)
    check("arrow keys move focus (R16)", page.active_index() == "10", str(page.active_index()))
    page.key(Keys.ARROW_LEFT)
    page.key(Keys.ARROW_LEFT)
    check("focus stops at the board edge", page.active_index() == "9")
    check("only one cell is in the tab order", page.count('#board .cell[tabindex="0"]') == 1)

    # --- win ---
    guard = 0
    while page.g("g.status") == "playing" and guard < 100:
        page.click(page.safe_hidden()[0])
        guard += 1
    check("win: status is won once all safe cells are open (R9)", page.g("g.status") == "won")
    check("win: face shows it", page.text("#face-glyph") == "\U0001F60E")
    check("win: counter reads 000 and every mine is flagged", page.text("#mines-left") == "000"
          and page.count("#board .cell.flagged") == 10)
    check("win: announced in words with the time (R13)",
          "Cleared in" in page.text("#status") and "New best" in page.text("#status"), page.text("#status"))
    t1 = page.text("#timer")
    page.wait(1300)
    check("win: timer stopped (R11)", page.text("#timer") == t1)
    check("win: stats updated (R14)", page.text("#stat-won").startswith("1 of 1") and page.text("#stat-best").endswith(" s"),
          page.text("#stat-won") + " / " + page.text("#stat-best"))
    page.click(m[1])
    check("win: board is locked", page.g("g.status") == "won")
    page.shot("03-won.png")

    # --- restart by keyboard ---
    page.key("r")
    check("R starts a new game (R12, R16)", page.g("g.status") == "ready" and page.text("#mines-left") == "010"
          and page.text("#timer") == "000" and page.count("#board .cell.open, #board .cell.flagged") == 0)
    check("new game: face is back to idle", page.text("#face-glyph") == "\U0001F642")

    # --- lose ---
    page.click(40)
    m = page.mines()
    wrong = page.safe_hidden()[0]
    page.right_click(wrong)
    page.right_click(m[2])
    page.click(m[0])
    check("lose: clicking a mine loses (R8)", page.g("g.status") == "lost")
    check("lose: the hit mine is highlighted", "exploded" in page.classes(m[0]))
    check("lose: every unflagged mine is shown", page.count("#board .cell.mine") == 9, str(page.count("#board .cell.mine")))
    check("lose: correct flag stays, wrong flag is marked", "wrong" in page.classes(wrong)
          and "wrong" not in page.classes(m[2]) and "flagged" in page.classes(m[2]))
    check("lose: face and words say so (R13)", page.text("#face-glyph") == "\U0001F635" and "hit a mine" in page.text("#status"))
    check("lose: stats count the game but not a win", page.text("#stat-won").startswith("1 of 2"), page.text("#stat-won"))
    opened = page.g("g.revealedCount")
    other = page.safe_hidden()[1]
    page.click(other)
    page.right_click(other)
    check("lose: board is locked", page.g("g.revealedCount") == opened and page.g("g.flagCount") == 2)
    page.shot("04-lost.png")

    page.click("#face")
    check("face button starts a new game (R12)", page.g("g.status") == "ready")

    # --- negative counter, middle click ---
    for i in range(11):
        page.right_click(i)
    check("counter goes negative with too many flags (R10)", page.text("#mines-left") == "-01", page.text("#mines-left"))
    check("flags before the first dig do not start the timer", page.text("#timer") == "000" and page.g("g.status") == "ready")
    page.key(Keys.F2)
    check("F2 starts a new game", page.g("g.flagCount") == 0)
    page.click(40)
    m = page.mines()
    target = page.ev(NUMBER_WITH_HIDDEN_SAFE_NEIGHBOUR)
    if target >= 0:
        nb = page.neighbours(target)
        for j in nb:
            if j in m:
                page.right_click(j)
        page.middle_click(target)
        check("middle-click chords (R7)", all(page.g(f"g.state[{j}]") != 0 for j in nb))

    # --- levels ---
    page.click('[data-level="intermediate"]')
    check("Intermediate: 16x16 with 40 mines (R1)", page.count("#board .cell") == 256 and page.text("#mines-left") == "040")
    page.click('[data-level="expert"]')
    check("Expert: 30x16 with 99 mines (R1)", page.count("#board .cell") == 480 and page.text("#mines-left") == "099")
    check("Expert: stats panel follows the board", "30 × 16, 99 mines" in page.text("#stat-board")
          and page.text("#stat-won") == "0 of 0", page.text("#stat-won"))
    check("Expert fits a 1280px window without scrolling", page.ev(WRAP_FITS))
    page.click(200)
    check("Expert: first click opens an area", page.count("#board .cell.open") >= 9)
    page.shot("05-expert.png")

    # --- custom ---
    page.click('[data-level="custom"]')
    check("Custom opens a dialog", page.ev("document.getElementById('custom-dialog').open"))
    page.fill("#c-cols", "12")
    page.fill("#c-rows", "8")
    page.fill("#c-mines", "200")
    page.click("#custom-form .primary")
    check("Custom: too many mines is refused with a reason",
          page.ev("document.getElementById('custom-dialog').open") and "1 to 87" in page.text("#c-hint"), page.text("#c-hint"))
    page.shot("06-custom-dialog.png")
    page.key("r")
    check("Custom: pressing R while the dialog is open does not restart the game behind it",
          page.ev("document.getElementById('custom-dialog').open") and page.g("g.status") == "playing")
    page.fill("#c-mines", "20")
    page.key(Keys.ENTER)
    check("Custom: a legal board starts (R1)", not page.ev("document.getElementById('custom-dialog').open")
          and page.count("#board .cell") == 96 and page.text("#mines-left") == "020" and page.pressed('[data-level="custom"]'),
          f"{page.count('#board .cell')} {page.text('#mines-left')}")
    page.click(0)
    page.click('[data-level="custom"]')
    page.key(Keys.ESCAPE)
    check("Custom: Escape cancels and keeps the game in progress", page.count("#board .cell") == 96 and page.g("g.status") == "playing")

    # --- reload keeps the game (R15) ---
    page.click('[data-level="intermediate"]')
    page.click(120)
    m = page.mines()
    page.right_click(m[0])
    page.wait(2200)
    snapshot = page.ev(BOARD_SNAPSHOT)
    before_timer = int(page.text("#timer"))
    page.reload()
    check("reload: the board comes back exactly (R15)", page.ev(BOARD_SNAPSHOT) == snapshot)
    check("reload: level, counter and timer come back", page.pressed('[data-level="intermediate"]')
          and page.text("#mines-left") == "039" and before_timer <= int(page.text("#timer")) <= before_timer + 2,
          f"{page.text('#mines-left')} {before_timer}->{page.text('#timer')}")
    page.wait(1300)
    check("reload: the timer keeps running", int(page.text("#timer")) > before_timer)
    page.click(m[1])
    check("reload: the restored game can still be lost", page.g("g.status") == "lost")
    page.reload()
    check("reload after a finished game gives a fresh board of the same level",
          page.g("g.status") == "ready" and page.count("#board .cell") == 256)
    check("stats survive reload (R14)", page.text("#stat-won").startswith("0 of 1"), page.text("#stat-won"))

    # --- theme (R19) ---
    start_theme = page.ev("document.documentElement.dataset.theme")
    check("light theme when the system is light", start_theme == "light", start_theme)
    page.click("#theme")
    flipped = page.ev("document.documentElement.dataset.theme")
    check("theme button flips to dark", flipped == "dark", flipped)
    page.reload()
    check("theme choice survives reload", page.ev("document.documentElement.dataset.theme") == "dark")
    page.click('[data-level="beginner"]')
    page.click(40)
    m = page.mines()
    page.right_click(m[0])
    page.shot("07-dark.png")
    page.click(m[1])
    page.shot("07b-dark-lost.png")

    # --- hostile storage ---
    page.ev("localStorage.setItem('minesweeper.v1', '{\"save\": {\"game\": {\"v\": 1, \"cols\": 9}}, \"stats\": 5, \"level\": 42}')")
    page.d.refresh()
    check("corrupt saved data falls back to a fresh Beginner game", page.g("g.status") == "ready" and page.count("#board .cell") == 81)
    page.ev("localStorage.setItem('minesweeper.v1', 'not json')")
    page.d.refresh()
    check("unparseable saved data falls back too", page.count("#board .cell") == 81)

    page.close()

    # --- system dark scheme, unseeded, in a fresh browser profile ---
    page = Page(1000, 800, scheme="dark")
    page.goto(url())
    check("follows the system dark scheme by default (R19)", page.ev("document.documentElement.dataset.theme") == "dark")
    page.click(40)
    check("unseeded (truly random) first click is safe and opens an area",
          page.g("g.status") in ("playing", "won") and page.count("#board .cell.open") >= 9)
    page.close()


def phone_run():
    print("phone: touch")
    page = Page(375, 740, mobile=True)
    page.goto(url("seed=11"))

    check("phone: page has no sideways scroll (R18)", page.ev(NO_PAGE_HSCROLL))
    size = page.ev("document.querySelector('#board .cell').getBoundingClientRect().width")
    check("phone: Beginner cells are finger-sized (>= 30px)", size >= 30, str(size))
    check("phone: whole Beginner board is visible without scrolling the frame", page.ev(WRAP_FITS))

    page.tap(40)
    check("phone: tap digs (R17)", page.g("g.status") == "playing" and page.count("#board .cell.open") >= 9,
          page.g("g.status"))
    hidden = page.safe_hidden()
    m = page.mines()
    page.long_press(m[0])
    check("phone: long-press flags and does not dig (R17)", "flagged" in page.classes(m[0])
          and page.g("g.status") == "playing" and page.text("#mines-left") == "009",
          " ".join(page.classes(m[0])) + " " + page.g("g.status"))
    page.long_press(m[0])
    check("phone: long-press again removes the flag", "flagged" not in page.classes(m[0]) and page.g("g.status") == "playing")
    page.tap(hidden[0])
    check("phone: a tap after a long-press still digs", page.g(f"g.state[{hidden[0]}]") == 1)

    page.tap("#mode-flag")
    check("phone: Flag mode switch turns on", page.pressed("#mode-flag") and not page.pressed("#mode-dig"))
    page.tap(m[1])
    check("phone: in Flag mode a tap flags (R17)", "flagged" in page.classes(m[1]) and page.g("g.status") == "playing")
    hidden = page.safe_hidden()
    if hidden:
        page.long_press(hidden[0])
        check("phone: in Flag mode a long-press digs", page.g(f"g.state[{hidden[0]}]") == 1)
    page.ev("window.scrollTo(0, 0)")
    page.shot("08-phone.png")
    page.tap("#mode-dig")

    page.tap('[data-level="expert"]')
    check("phone: Expert selected by tap", page.count("#board .cell") == 480)
    check("phone: Expert keeps the page from scrolling sideways (R18)", page.ev(NO_PAGE_HSCROLL))
    check("phone: Expert board scrolls inside its frame", not page.ev(WRAP_FITS))
    size = page.ev("document.querySelector('#board .cell').getBoundingClientRect().width")
    check("phone: Expert cells stay tappable (>= 24px)", size >= 24, str(size))
    page.tap(200)
    page.ev("window.scrollTo(0, 0)")
    page.shot("09-phone-expert.png")
    page.close()


def main():
    desktop_run()
    phone_run()
    check("no console errors, warnings or failed requests", not problems, "; ".join(problems[:5]))
    failed = [r for r in results if not r[1]]
    print(f"\n{len(results) - len(failed)} passed, {len(failed)} failed  ({BASE})")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
