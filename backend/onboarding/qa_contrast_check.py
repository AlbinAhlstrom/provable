"""
QA contrast check: text the audience cannot see is a defect, measured rather than judged.

The audit reads, for each piece of text the page shows, the colour it is drawn in and the colour behind it, and
computes the contrast between the two (the ratio of their luminances, 1 for the same colour, 21 for black on white).

- Text whose contrast is below `FAINT_BELOW` is all but invisible: a defect, quoted with both colours and the measured
  contrast so the one rework knows what to change. The bar sits far under what is asked of comfortable reading, so
  muted helper text passes; only text in nearly the tone of its background is caught.
- Text the check cannot measure is skipped: text or a background that is partly transparent, text over an image or a
  gradient. That is the check's limit, not the page's fault.
- One line per pair of colours, however many texts share it: one cause, one defect.
"""

from collections import Counter
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence

from pipeline_trace import traced

FAINT_BELOW = 1.5
READABLE_FROM = 3  # what the rework is asked to reach: well clear of the bar, so a small change is not enough
SAMPLES_QUOTED = 3

_CONTRAST_SCRIPT = r"""
var rgba = function (value) {
    var m = /rgba?\(([^)]+)\)/.exec(value || '');
    if (!m) return null;
    var p = m[1].split(/[,\s\/]+/).filter(Boolean).map(parseFloat);
    return {rgb: [p[0], p[1], p[2]], alpha: p.length > 3 ? p[3] : 1};
};
var samples = [];
var walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
for (var node = walker.nextNode(); node; node = walker.nextNode()) {
    var text = node.textContent.trim();
    var el = node.parentElement;
    if (!text || !el) continue;
    var rect = el.getBoundingClientRect();
    if (rect.width < 4 || rect.height < 4) continue;
    var style = getComputedStyle(el);
    if (style.visibility === 'hidden' || style.display === 'none') continue;
    var color = rgba(style.color);
    if (!color || color.alpha < 1) continue;
    var background = null;
    var measurable = true;
    for (var up = el; up; up = up.parentElement) {
        var s = getComputedStyle(up);
        if (parseFloat(s.opacity) < 1 || s.backgroundImage !== 'none') { measurable = false; break; }
        var bg = rgba(s.backgroundColor);
        if (bg && bg.alpha > 0) {
            if (bg.alpha < 1) measurable = false;
            else background = bg.rgb;
            break;
        }
    }
    if (!measurable) continue;
    samples.push({text: text.slice(0, 30), color: color.rgb, background: background || [255, 255, 255]});
}
return samples;
"""


@dataclass
class ContrastCheck:
    """What measuring the page's text showed. Defects fail the audit; warnings are reported with the verdict."""
    defects: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


def _luminance(rgb: Sequence[float]) -> float:
    channels = []
    for value in rgb[:3]:
        c = value / 255
        channels.append(c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def contrast_ratio(first: Sequence[float], second: Sequence[float]) -> float:
    """The contrast between two colours: 1 when they are the same, 21 for black and white."""
    lighter, darker = sorted((_luminance(first), _luminance(second)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


def _between(background: Sequence[float], texts: List[Sequence[float]]) -> Optional[List[int]]:
    """The background's own hue, made darker or lighter until every one of `texts` reaches READABLE_FROM on it: the
    nearest such tone to what the background is now. None when no tone carries them all. A writer cannot measure a
    colour, so it is handed one."""
    candidates = []
    for step in range(0, 101):
        for toward in (0, 255):
            tone = [int(round(c + (toward - c) * step / 100)) for c in background[:3]]
            if all(contrast_ratio(text, tone) >= READABLE_FROM for text in texts):
                candidates.append((step, tone))
        if candidates:
            return min(candidates)[1]
    return None


def _hex(rgb: Sequence[float]) -> str:
    return "#" + "".join(f"{int(round(v)):02x}" for v in rgb[:3])


def verdict_from_samples(device: str, samples: List[Dict[str, Any]]) -> ContrastCheck:
    """One defect per pair of colours too close to tell apart, the pair touching the most texts first."""
    texts: Dict[tuple, List[str]] = {}
    for sample in samples:
        pair = (tuple(sample["color"][:3]), tuple(sample["background"][:3]))
        if contrast_ratio(*pair) < FAINT_BELOW:
            texts.setdefault(pair, []).append(str(sample.get("text") or ""))
    check = ContrastCheck()
    for pair, _ in Counter({pair: len(found) for pair, found in texts.items()}).most_common():
        found = texts[pair]
        quoted = ", ".join(f'"{t}"' for t in list(dict.fromkeys(found))[:SAMPLES_QUOTED])
        others = sorted({tuple(s["color"][:3]) for s in samples
                         if tuple(s["background"][:3]) == pair[1] and tuple(s["color"][:3]) != pair[0]
                         and contrast_ratio(s["color"], pair[1]) >= READABLE_FROM})
        way_out = (f"The same background also carries text in {', '.join(_hex(c) for c in others)}, which it must keep "
                   f"readable, so the background has to become a tone between the two: clearly darker than its light "
                   f"text and clearly lighter than its dark text. " if others else "")
        proposed = _between(pair[1], [pair[0]] + others) if others else None
        if proposed:
            way_out += f"All of that text can be read on this background made a middle tone, for example {_hex(proposed)}. "
        elsewhere = sorted({tuple(s["background"][:3]) for s in samples if tuple(s["color"][:3]) == pair[0]
                            and contrast_ratio(pair[0], s["background"]) >= READABLE_FROM})
        if elsewhere:
            way_out += (f"This text colour reads well on {', '.join(_hex(b) for b in elsewhere)}, so keep the text one "
                        f"colour everywhere it is shown and change this background. ")
        check.defects.append(
            f"[{device}] Unreadable text: {len(found)} text(s) (such as {quoted}) are drawn in {_hex(pair[0])} on a "
            f"background of {_hex(pair[1])}, a contrast of {contrast_ratio(*pair):.1f} to 1. {way_out}"
            f"Change the text colour or the background until the contrast is at least {READABLE_FROM:g} to 1 on "
            f"every background the text is shown on")
    return check


@traced("qa.contrast_check")
def measure_contrast(driver, device: str) -> ContrastCheck:
    """Measures the text of the page the driver has open. A check that could not run is a warning."""
    try:
        samples = driver.execute_script(_CONTRAST_SCRIPT)
    except Exception as err:
        return ContrastCheck(warnings=[f"[{device}] the contrast check could not run: {type(err).__name__}: {str(err)[:200]}"])
    return verdict_from_samples(device, list(samples or []))
