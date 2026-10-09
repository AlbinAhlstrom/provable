"""
QA text check: an escape the page shows letter by letter is a defect, read from the page rather than judged.

A Unicode escape (a backslash, `u` and four hex digits) is only read inside a JavaScript string, and an HTML entity
only in markup. Written anywhere else (an escape as bare JSX text, an entity inside a string) the page shows its
letters. The page still builds and fits every screen, so only reading its text finds it.

- Each escape or entity found in the text the page shows is a defect, quoted with the text it stands in, so the one
  rework knows what to change. One line per escape, however many texts show it.
- Text inside `code`, `pre`, `kbd`, `samp` and form fields is not read: there an escape may be the content itself.
"""

import re
from dataclasses import dataclass, field
from typing import Dict, List

from pipeline_trace import traced

SAMPLES_QUOTED = 3
_ESCAPE = re.compile(r"\\u[0-9a-fA-F]{4}|\\u\{[0-9a-fA-F]{1,6}\}|\\x[0-9a-fA-F]{2}|&#x?[0-9a-fA-F]{2,6};|&[a-z]{2,8};")

_TEXT_SCRIPT = r"""
var texts = [];
var walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
for (var node = walker.nextNode(); node; node = walker.nextNode()) {
    var text = node.textContent.trim();
    var el = node.parentElement;
    if (!text || !el || el.closest('code, pre, kbd, samp, textarea, script, style')) continue;
    var style = getComputedStyle(el);
    if (style.visibility === 'hidden' || style.display === 'none') continue;
    texts.push(text.slice(0, 60));
}
return texts;
"""


@dataclass
class TextCheck:
    """What reading the page's text showed. Defects fail the audit; warnings are reported with the verdict."""
    defects: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


def verdict_from_texts(device: str, texts: List[str]) -> TextCheck:
    """One defect per escape shown as letters, the escape touching the most texts first."""
    shown_in: Dict[str, List[str]] = {}
    for text in texts:
        for escape in dict.fromkeys(_ESCAPE.findall(str(text or ""))):
            shown_in.setdefault(escape, []).append(str(text))
    check = TextCheck()
    for escape, found in sorted(shown_in.items(), key=lambda item: -len(item[1])):
        quoted = ", ".join(f'"{t}"' for t in list(dict.fromkeys(found))[:SAMPLES_QUOTED])
        check.defects.append(
            f"[{device}] Escape shown as letters: {len(found)} text(s) (such as {quoted}) show the letters of "
            f"{escape} instead of the character it stands for. A backslash escape is only read inside a JavaScript "
            f"string (in JSX: {{'...'}}), an entity only in markup; write it where it is read, or write the character "
            f"itself")
    return check


@traced("qa.text_check")
def read_text(driver, device: str) -> TextCheck:
    """Reads the text of the page the driver has open. A check that could not run is a warning."""
    try:
        texts = driver.execute_script(_TEXT_SCRIPT)
    except Exception as err:
        return TextCheck(warnings=[f"[{device}] the text check could not run: {type(err).__name__}: {str(err)[:200]}"])
    return verdict_from_texts(device, list(texts or []))
