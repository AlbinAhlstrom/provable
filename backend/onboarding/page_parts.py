"""The parts of a page: what its plan names by role and name.

The plan's read-out list (`ProductContract.blueprint`, section 3) has one line per part a person meets:

    - <what it is> · <role> · "<the name it is read out by>"

That list is the page's extent. It is read here once and used twice:

    parts_block    the page's writer is shown it as the parts of the page, and answers where it writes each one
                   before it writes the files (prompts/presentation_projection_synthesis.md)
    missing_parts  the written page is looked through for every part; one that is not there is a QA defect, so it
                   goes through the single rework QA allows (page_gates.py)
    present_parts  the page as opened in a browser is looked through the same way: none of its parts on screen is
                   a page that never gets going (qa_opening_check.py)

The look-through reads source, not a rendered page: a dialog or the items of a menu are not on screen until a step
brings them up, and they are the parts a hurried page leaves out. It is a presence check and claims no more: a part
is there when the page has its role (the attribute, or an element that carries the role natively) and the fixed
words of its name, in any case. Whether the part works is what the page tests are for.
"""
import re
from dataclasses import dataclass
from typing import Iterable, List

_LINE = re.compile(r'^- (?P<what>.+?) · (?P<role>[\w-]+) · "(?P<name>.*)"[ \t]*$', re.MULTILINE)
_SLOT = re.compile(r"\{[^{}]*\}")       # the part of a name a field's value fills
_WORDS = re.compile(r"\w[\w .'-]*\w|\w")

# Elements that carry a role without the attribute
_NATIVE = {
    "button": r"<button\b",
    "textbox": r"<(?:input|textarea)\b",
    "checkbox": r"""type=\{?["']checkbox["']""",
    "dialog": r"<dialog\b",
    "heading": r"<h[1-6]\b",
    "list": r"<[uo]l\b",
    "listitem": r"<li\b",
    "img": r"<(?:img|svg)\b",
    "status": r"<output\b",
    "grid": r"<table\b",
    "gridcell": r"<td\b",
}

MISSING = "[Missing part] "


@dataclass(frozen=True)
class Part:
    what: str
    role: str
    name: str  # as the plan writes it; `{field}` stands for a value

    def line(self) -> str:
        return f'{self.what} · {self.role} · "{self.name}"'


def parts_of(plan: str) -> List[Part]:
    """The parts the plan names, in its order."""
    return [Part(found["what"].strip(), found["role"], found["name"]) for found in _LINE.finditer(plan or "")]


def parts_block(plan: str) -> str:
    """The parts as the page's writer is shown them."""
    parts = parts_of(plan)
    if not parts:
        return "The blueprint names no parts by role and name: the parts are the ones its sections describe."
    return f"The page has these parts ({len(parts)}):\n" + "\n".join(f"- {part.line()}" for part in parts)


def _has_role(role: str, source: str) -> bool:
    if re.search(r"""role=\{?["']""" + re.escape(role) + r"""["']""", source):
        return True
    native = _NATIVE.get(role)
    return bool(native and re.search(native, source))


def _has_name(name: str, source: str) -> bool:
    """The fixed words of the name, as whole words in any case: a page may build a name from a field's value
    (a status `open` shown as "Open"), and then the source holds the word in the value's own case."""
    fixed = [words for piece in _SLOT.split(name) for words in _WORDS.findall(piece)]
    return all(re.search(r"(?<!\w)" + re.escape(words) + r"(?!\w)", source, re.IGNORECASE) for words in fixed)


def present_parts(parts: Iterable[Part], sources: Iterable[str]) -> List[Part]:
    """The parts found in the sources: the page's files, or the document of the page as opened."""
    source = "\n".join(sources)
    return [part for part in parts if _has_role(part.role, source) and _has_name(part.name, source)]


def missing_parts(parts: Iterable[Part], sources: Iterable[str]) -> List[str]:
    """One defect for each part the page's files do not have."""
    parts = list(parts)
    found = present_parts(parts, sources)
    return [f'{MISSING}The plan names "{part.what}" ({part.role}, read out as "{part.name}") and the page does not '
            f'have it. Write it as the plan describes it, with the step that brings it up.'
            for part in parts if part not in found]
