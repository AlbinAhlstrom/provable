"""
QA access check: a control or image that has no name is a defect, read from the page rather than judged.

A button that holds only an icon, a field with no label, and a picture with no `alt`
all build, fit every screen and look right, yet a screen reader announces them as nothing at all. Only reading the
page's accessibility names finds them.

- Each kind of nameless element is one defect, with how many there are and a few of them described by tag and place,
  so the one rework knows what to name.
- Hidden elements and decorative images (`alt=""`, `role="presentation"`) are not read.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List

from pipeline_trace import traced

SAMPLES_QUOTED = 3

_KIND_ADVICE = {
    "control": "give it visible text, an `aria-label`, or an `aria-labelledby`",
    "field": "bind a `<label htmlFor>` to its `id`, or give it an `aria-label`",
    "image": "give it an `alt` that says what it shows, or `alt=\"\"` when it is only decoration",
}

_ACCESS_SCRIPT = r"""
var found = [];
function shown(el) {
    var style = getComputedStyle(el);
    var rect = el.getBoundingClientRect();
    return style.visibility !== 'hidden' && style.display !== 'none' && rect.width > 0 && rect.height > 0;
}
function describe(el) {
    var text = (el.id ? '#' + el.id : '') + (el.className && typeof el.className === 'string'
        ? '.' + el.className.trim().split(/\s+/).slice(0, 2).join('.') : '');
    return el.tagName.toLowerCase() + text.slice(0, 60);
}
function labelled(el) {
    if ((el.getAttribute('aria-label') || '').trim()) return true;
    var by = el.getAttribute('aria-labelledby');
    if (by && by.split(/\s+/).some(function (id) {
        var ref = document.getElementById(id);
        return ref && ref.textContent.trim();
    })) return true;
    return false;
}
document.querySelectorAll('button, a[href], [role="button"]').forEach(function (el) {
    if (!shown(el) || labelled(el)) return;
    var text = (el.innerText || el.textContent || '').trim();
    var img = el.querySelector('img[alt]:not([alt=""])');
    if (text || img || (el.getAttribute('title') || '').trim()) return;
    found.push({kind: 'control', where: describe(el)});
});
document.querySelectorAll('input, select, textarea').forEach(function (el) {
    var type = (el.getAttribute('type') || '').toLowerCase();
    if (type === 'hidden' || type === 'submit' || type === 'button' || type === 'reset' || !shown(el)) return;
    if (labelled(el) || (el.labels && el.labels.length && Array.from(el.labels).some(function (l) { return l.textContent.trim(); }))) return;
    if ((el.getAttribute('title') || '').trim()) return;
    found.push({kind: 'field', where: describe(el)});
});
document.querySelectorAll('img').forEach(function (el) {
    if (!shown(el) || el.getAttribute('alt') !== null || el.getAttribute('role') === 'presentation') return;
    found.push({kind: 'image', where: describe(el)});
});
return found;
"""


@dataclass
class AccessCheck:
    """What reading the page's names showed. Defects fail the audit; warnings are reported with the verdict."""
    defects: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


def verdict_from_elements(device: str, elements: List[Dict[str, Any]]) -> AccessCheck:
    """One defect per kind of nameless element, with a few of them described."""
    by_kind: Dict[str, List[str]] = {}
    for element in elements:
        kind = str(element.get("kind") or "")
        if kind in _KIND_ADVICE:
            by_kind.setdefault(kind, []).append(str(element.get("where") or "?"))
    check = AccessCheck()
    for kind in _KIND_ADVICE:  # a fixed order keeps the report steady between runs
        found = by_kind.get(kind)
        if not found:
            continue
        noun = {"control": "button(s) or link(s)", "field": "form field(s)", "image": "image(s)"}[kind]
        quoted = ", ".join(f"`{w}`" for w in list(dict.fromkeys(found))[:SAMPLES_QUOTED])
        check.defects.append(
            f"[{device}] Nameless element: {len(found)} {noun} (such as {quoted}) have no name a screen reader "
            f"can announce; {_KIND_ADVICE[kind]}")
    return check


@traced("qa.access_check")
def read_names(driver, device: str) -> AccessCheck:
    """Reads the names of the controls, fields and images of the page the driver has open. A check that could not run
    is a warning."""
    try:
        elements = driver.execute_script(_ACCESS_SCRIPT)
    except Exception as err:
        return AccessCheck(warnings=[f"[{device}] the access check could not run: {type(err).__name__}: {str(err)[:200]}"])
    return verdict_from_elements(device, list(elements or []))
