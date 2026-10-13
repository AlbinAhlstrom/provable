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
    locators_module  a page test finds a part through a function written from its line (`tests/e2e/parts.py`), so
                   the role and the name are copied into a test by code and not by the test's writer

The look-through reads source, not a rendered page: a dialog or the items of a menu are not on screen until a step
brings them up, and they are the parts a hurried page leaves out. It is a presence check and claims no more: a part
is there when the page has its role (the attribute, or an element that carries the role natively) and the fixed
words of its name, in any case. Whether the part works is what the page tests are for.
"""
import json
import keyword
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


# ── a part as a page test finds it ───────────────────────────────────────────

_SLOT_NAME = re.compile(r"\{([^{}]*)\}")


def _identifier(words: str, fallback: str) -> str:
    """Words as a name Python accepts: lower case, joined by underscores, never one of Python's own words."""
    text = re.sub(r"\W+", "_", words.strip().lower()).strip("_") or fallback
    if text[0].isdigit():
        text = f"{fallback}_{text}"
    return text + "_" if keyword.iskeyword(text) or text == "page" else text


@dataclass(frozen=True)
class PartFunction:
    """The function a page test finds a part through."""
    name: str
    part: Part
    slots: List[str]  # the values the part's name is built from, as the function's arguments

    def call(self) -> str:
        return f"parts.{self.name}(page{''.join(f', {slot}=...' for slot in self.slots)})"

    def _name_expression(self) -> str:
        pieces = _SLOT_NAME.split(self.part.name)  # fixed words and slot names, in turn
        terms = [json.dumps(piece) if at % 2 == 0 else f"str({_identifier(piece, 'value')})"
                 for at, piece in enumerate(pieces) if piece or at % 2]
        return " + ".join(terms) or '""'

    def source(self) -> str:
        takes = "page" + (", *, " + ", ".join(self.slots) if self.slots else "")
        return (f"# {self.part.what}: {self.part.role} \"{self.part.name}\"\n"
                f"def {self.name}({takes}):\n"
                f"    return page.get_by_role({json.dumps(self.part.role)}, name={self._name_expression()}, exact=True)\n")


def part_functions(parts: Iterable[Part]) -> List[PartFunction]:
    """One function per part, named after what the part is; two parts called the same are told apart by role."""
    functions: List[PartFunction] = []
    taken = set()
    for part in parts:
        name = _identifier(part.what, "part")
        if name in taken:
            name = f"{name}_{_identifier(part.role, 'part')}"
        count = 2
        while name in taken:
            name, count = f"{name.rstrip('0123456789_')}_{count}", count + 1
        taken.add(name)
        slots = list(dict.fromkeys(_identifier(slot, "value") for slot in _SLOT_NAME.findall(part.name)))
        functions.append(PartFunction(name, part, slots))
    return functions


def locators_module(parts: Iterable[Part]) -> str:
    """`tests/e2e/parts.py`: every part of the plan as a function that returns its locator."""
    return ('"""The parts of the page, each found by the role and the whole name the page\'s plan gives it.\n\n'
            "Written by the engine from the plan (onboarding/page_parts.py); a change made here is overwritten.\n"
            '`page` is the page, or a locator to look inside.\n"""\n\n\n'
            + "\n\n".join(function.source() for function in part_functions(parts)))


def locators_block(parts: Iterable[Part]) -> str:
    """What a page test's writer is told of the functions; empty when the plan names no part."""
    functions = part_functions(parts)
    if not functions:
        return ""
    listed = "\n".join(f'- `{f.call()}`: {f.part.role} "{f.part.name}"' for f in functions)
    return ("## The parts of the page\n`import parts` gives one function for each part the page's plan names by "
            "role and name. It returns the locator of that part, found by exactly that role and that whole name, "
            "with each value in braces handed in as the argument named after it:\n\n" + listed + "\n\n"
            "The first argument is the page, or a locator to look inside. A part listed here is found through its "
            "function, with the values the records you arranged give it, and by no locator of your own. What is "
            "said above about finding a control holds for everything else: a message, a text, every control of one "
            "role at once.\n")


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
