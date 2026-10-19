"""The parts of a page: what its plan names by role and name.

The plan's read-out list (`ProductContract.blueprint`, section 3) has one line per part a person meets:

    - <what it is> · <role> · "<the name it is read out by>"[ · <state> when <condition>[; ...]]

A state (`STATES`: pressed, checked, selected, expanded, disabled) is given to the element by the page's call, handed
true or false, as the attribute a screen reader reads it by, and a test hands it in to find the part in it.

That list is the page's extent. It is read here once, and every use of it is written from it by code:

    props_module   the page gets a part's role and name by spreading a call on its element (`src/api/parts.ts`),
                   so neither is copied into the page by its writer
    parts_block    the page's writer is shown the parts of the page, each with its call, and answers where it
                   writes each one before it writes the files (prompts/presentation_projection_synthesis.md); under a
                   part whose name holds a value the plan writes a way of its own (`shown value`), how it is written,
                   which a page test's writer is shown the same way; a number the plan writes in a fixed form
                   (`written as 3 digits`) is written in it by the call, in both modules, handed the number
    missing_parts  the written page is looked through for the call of every part; one that is not there is a QA
                   defect, so it goes through the single rework QA allows (page_gates.py)
    present_parts  the page as opened in a browser is looked through the same way: none of its parts on screen is
                   a page that never gets going (qa_opening_check.py)
    locators_module  a page test finds a part through a function written from its line (`tests/e2e/parts.py`), so
                   the role and the name are copied into a test by code and not by the test's writer

The look-through of the written page reads source, not a rendered page: a dialog or the items of a menu are not on
screen until a step brings them up, and they are the parts a hurried page leaves out. A part is there when its call
is: an element that only looks like the part (a role of its own choosing, a name no line gives) is found by no test.
The opened page is looked through by role and the fixed words of a name, in any case, which is what the calls put
there. Both are presence checks and claim no more: whether the part works is what the page tests are for.
"""
import json
import keyword
import re
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple

_LINE = re.compile(r'^- (?P<what>.+?) · (?P<role>[\w-]+) · "(?P<name>.*?)"(?: · (?P<states>[a-z]+ when .+?))?[ \t]*$',
                   re.MULTILINE)
_STATE = re.compile(r"(?P<word>[a-z]+) when (?P<when>.+?)\s*(?:;\s*(?=[a-z]+ when )|$)")
_SLOT = re.compile(r"\{[^{}]*\}")       # the part of a name a field's value fills
_WORDS = re.compile(r"\w[\w .'-]*\w|\w")

# Elements that carry a role without the attribute
FILE_NAME = "parts.ts"  # beside the API clients, as the page imports it

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

# How a number is written in each form, in Python: the tests' module holds this source and `Form.write` runs it
_FORMS_PY = (
    "def _digits(value, count):\n"
    '    """A whole number in `count` characters, zeros filled after its sign: 7 as "007", -3 as "-03"."""\n'
    "    number = int(value)\n"
    '    return ("-" if number < 0 else "") + str(abs(number)).zfill(count - 1 if number < 0 else count)\n\n\n'
    "def _decimals(value, count):\n"
    '    """A number with `count` digits after the point: 5 as "5.00"."""\n'
    '    return f"{float(value):.{count}f}"\n\n\n')
_FORM_HELPERS: Dict[str, object] = {}
exec(_FORMS_PY, _FORM_HELPERS)

# The states a part can be told apart by, each with the attribute that gives it to an element and the roles that
# have it: what a screen reader reads out, and what a test finds a part in that state by (prompts/product_contract.md)
STATES = {
    "pressed": ("aria-pressed", ("button",)),
    "checked": ("aria-checked", ("checkbox", "menuitemcheckbox", "menuitemradio")),
    "selected": ("aria-selected", ("gridcell",)),
    "expanded": ("aria-expanded", ("button", "menuitem")),
    "disabled": ("aria-disabled", ("button", "textbox", "checkbox", "menuitem", "menuitemcheckbox", "menuitemradio",
                                   "gridcell")),
}


@dataclass(frozen=True)
class State:
    word: str  # one of STATES
    when: str  # when it holds, in the plan's words


@dataclass(frozen=True)
class Part:
    what: str
    role: str
    name: str  # as the plan writes it; `{field}` stands for a value
    states: Tuple[State, ...] = ()

    def line(self) -> str:
        return f'{self.what} · {self.role} · "{self.name}"' + "".join(
            f"{' · ' if at == 0 else '; '}{state.word} when {state.when}" for at, state in enumerate(self.states))

    def state_errors(self) -> List[str]:
        """Each state of the part that no role has, or that its role lacks."""
        return [f"{self.line()}: `{state.word}` is not a state of a {self.role} ("
                + ", ".join(word for word, (_, roles) in STATES.items() if self.role in roles) + ")"
                if state.word in STATES else
                f"{self.line()}: `{state.word}` is no state (" + ", ".join(STATES) + ")"
                for state in self.states if self.role not in STATES.get(state.word, ("", ()))[1]]


def parts_of(plan: str) -> List[Part]:
    """The parts the plan names, in its order."""
    return [Part(found["what"].strip(), found["role"], found["name"],
                 tuple(State(s["word"], s["when"]) for s in _STATE.finditer(found["states"] or "")))
            for found in _LINE.finditer(plan or "")]


def part_of_entry(entry: str) -> Optional[Part]:
    """The part an entry of the contract's `read_out` names, or None for an entry that names no part."""
    found = parts_of(f"- {entry}")
    return found[0] if found else None


_SHOWN = re.compile(r"^- shown value: (?P<name>\w[\w ]*?) = (?P<how>.+?)[ \t]*$", re.MULTILINE)
# The forms a shown value may be written in, by the phrase its entry ends with (prompts/product_contract.md)
_FORM = re.compile(r";\s*written as (?P<count>\d+) (?P<kind>digits|decimals)\s*\.?$")


@dataclass(frozen=True)
class Form:
    """How a number is written inside a name: `digits`, a whole number filled with zeros after its sign to `count`
    characters; `decimals`, a number with `count` digits after the point. With the form told to both writers beside
    the part, the page wrote "Mines left 10" where the tests looked for "010": so both part modules write it, handed
    the number."""
    kind: str
    count: int

    def write(self, value: float) -> str:
        """The value in this form, by the helper the tests' module runs."""
        return _FORM_HELPERS[f"_{self.kind}"](value, self.count)

    def said(self) -> str:
        examples = (7, -3) if self.kind == "digits" else (5,)
        return f"with {self.count} {self.kind} (" + ", ".join(f'{n} as "{self.write(n)}"' for n in examples) + ")"


def misformed(how: str) -> bool:
    """Whether a shown value's definition says it is written in a form that is neither of the forms."""
    return "written as" in how and not _FORM.search(how)


def value_forms(plan: str) -> Dict[str, Form]:
    """The shown values written in a fixed form, by the name a part's name gives them."""
    forms = {}
    for found in _SHOWN.finditer(plan or ""):
        form = _FORM.search(found["how"])
        if form:
            forms[identifier(found["name"], "value")] = Form(form["kind"], int(form["count"]))
    return forms


_FIELD_WORDING = re.compile(r'^- `(?P<field>\w+\.(?P<name>\w+))` (?P<value>[^:\n]+?):[^\n]*?shown as "(?P<wording>[^"]*)"',
                            re.MULTILINE)


def _wording_tables(plan: str) -> Dict[str, Dict[str, Dict[str, str]]]:
    """`<field>_wording` -> `Record.field` -> value -> wording, for every field the plan words."""
    tables: Dict[str, Dict[str, Dict[str, str]]] = {}
    for found in _FIELD_WORDING.finditer(plan or ""):
        table = tables.setdefault(f"{found['name']}_wording", {}).setdefault(found["field"], {})
        table[found["value"].strip()] = found["wording"]
    return tables


@dataclass(frozen=True)
class Wording:
    """A field's wordings, put into a part's name by its call: the call is handed the value the record holds."""
    field: str                 # `Record.field`
    table: Dict[str, str]      # value -> how the person is shown it

    @property
    def argument(self) -> str:
        return self.field.split(".", 1)[1]

    def listed(self) -> str:
        return ", ".join(f'{value} "{wording}"' for value, wording in self.table.items())


def field_wordings(plan: str) -> Dict[str, Wording]:
    """The `{field wording}` slots (`<field>_wording`) whose wordings are one list: a field of one record, or fields
    of several that word their values alike. Where they differ, which record a part shows is the writer's to say."""
    return {slot: Wording(next(iter(fields)), next(iter(fields.values())))
            for slot, fields in _wording_tables(plan).items()
            if all(table == next(iter(fields.values())) for table in fields.values())}


def shown_values(plan: str) -> Dict[str, str]:
    """The values the plan writes a way of its own, by the name a part's name gives them: each `- shown value:
    <name> = <how>`, and for a field with `shown as` wordings, `<field>_wording` (the contract's `{field wording}`)."""
    values = {slot: "; ".join(f"the wording of `{field}`: " + Wording(field, table).listed()
                              for field, table in fields.items())
              for slot, fields in _wording_tables(plan).items()}
    return {**values, **{identifier(found["name"], "value"): _FORM.sub("", found["how"]).strip()
                         for found in _SHOWN.finditer(plan or "")}}


def _how_shown(function: "PartFunction", shown: Dict[str, str]) -> str:
    """Under a part, how each value its name is built from is written: the page puts it into the name and a test
    looks for it as the person is shown it, both from this one definition. A name and its definition stood far
    apart in the plan, and the page wrote a bare number into a name the plan writes with three digits."""
    lines = []
    for slot in function.slots:
        worded = function.wordings.get(slot)
        if worded:
            lines.append(f"\n  `{worded.argument}` is handed in as `{worded.field}` holds it, and the call puts in its "
                         f"wording: {worded.listed()}")
        elif slot in (function.forms or {}):
            lines.append(f"\n  `{slot}` is handed in as a number, and the call writes it {function.forms[slot].said()}"
                         + (f": {shown[slot]}" if slot in shown else ""))
        elif slot in shown:
            lines.append(f"\n  `{slot}` is handed in as the person is shown it: {shown[slot]}")
    lines += [f"\n  `{state.word}` is handed in as true when {state.when}, else false" for state in function.part.states]
    return "".join(lines)


def parts_block(plan: str) -> str:
    """The parts as the page's writer is shown them."""
    functions, shown = part_functions(parts_of(plan), field_wordings(plan), value_forms(plan)), shown_values(plan)
    if not functions:
        return "The blueprint names no parts by role and name: the parts are the ones its sections describe."
    return (f"The page has these parts ({len(functions)}):\n"
            + "\n".join(f"- {f.part.line()} · `{f.spread()}`" + _how_shown(f, shown) for f in functions))


# ── a part as a page test finds it ───────────────────────────────────────────

_SLOT_NAME = re.compile(r"\{([^{}]*)\}")


def identifier(words: str, fallback: str) -> str:
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
    slots: List[str]  # the values the part's name is built from
    wordings: Optional[Dict[str, Wording]] = None  # slot -> the field whose wording the call puts in for it
    forms: Optional[Dict[str, Form]] = None        # slot -> the form the call writes its number in

    def _worded(self, slot: str) -> Optional[Wording]:
        return (self.wordings or {}).get(slot)

    @property
    def arguments(self) -> List[str]:
        """What the call is handed: each slot, or for a field's wording the field's value."""
        return [worded.argument if (worded := self._worded(slot)) else slot for slot in self.slots]

    @property
    def states(self) -> List[str]:
        return [state.word for state in self.part.states]

    def call(self) -> str:
        return f"parts.{self.name}(page{''.join(f', {argument}=...' for argument in self.arguments + self.states)})"

    @property
    def page_name(self) -> str:
        """The name of the call the page spreads: the same words, joined the way the page's language joins them."""
        first, *rest = self.name.split("_")
        return first + "".join(word[:1].upper() + word[1:] for word in rest) + ("_" if self.name.endswith("_") else "")

    def spread(self) -> str:
        handed = self.arguments + self.states
        values = "{ " + ", ".join(handed) + " }" if handed else ""
        return "{..." + f"parts.{self.page_name}({values})" + "}"

    def props(self) -> str:
        """The call as `src/api/parts.ts` defines it."""
        pieces = _SLOT_NAME.split(self.part.name)
        terms = [json.dumps(piece) if at % 2 == 0 else self._term(identifier(piece, "value"), "String(v.{})",
                                                                     "worded({}, v.{})", "{}(v.{}, {})")
                 for at, piece in enumerate(pieces) if piece or at % 2]
        handed = [f"{argument}: Value" for argument in self.arguments] + [f"{word}: boolean" for word in self.states]
        takes = "v: { " + "; ".join(handed) + " }" if handed else ""
        states = "".join(f", '{STATES[word][0]}': v.{word}" for word in self.states)
        return (f"  /** {self.part.what}: {self.part.role} \"{self.part.name}\" */\n"
                f"  {self.page_name}: ({takes}) => "
                f"({{ role: {json.dumps(self.part.role)}, 'aria-label': {' + '.join(terms) or json.dumps('')}{states} }}),\n")

    def _name_expression(self) -> str:
        pieces = _SLOT_NAME.split(self.part.name)  # fixed words and slot names, in turn
        terms = [json.dumps(piece) if at % 2 == 0 else self._term(identifier(piece, "value"), "str({})",
                                                                     "_worded({}, {})", "_{}({}, {})")
                 for at, piece in enumerate(pieces) if piece or at % 2]
        return " + ".join(terms) or '""'

    def _term(self, slot: str, plain: str, worded: str, formed: str) -> str:
        """A value of the name: as handed in, for a field's wording the wording the plan gives the value, or for a
        number with a form of its own the number written in it."""
        wording, form = self._worded(slot), (self.forms or {}).get(slot)
        if wording:
            return worded.format(json.dumps(wording.table, ensure_ascii=False), wording.argument)
        return formed.format(form.kind, slot, form.count) if form else plain.format(slot)

    def source(self) -> str:
        handed = self.arguments + [f"{word}=None" for word in self.states]
        takes = "page" + (", *, " + ", ".join(handed) if handed else "")
        states = (", **_in_states(" + ", ".join(f"{word}={word}" for word in self.states) + ")") if self.states else ""
        return (f"# {self.part.line()}\n"
                f"def {self.name}({takes}):\n"
                f"    return page.get_by_role({json.dumps(self.part.role)}, name={self._name_expression()}, exact=True"
                f"{states})\n")


def part_functions(parts: Iterable[Part], wordings: Optional[Dict[str, Wording]] = None,
                   forms: Optional[Dict[str, Form]] = None) -> List[PartFunction]:
    """One function per part, named after what the part is; two parts called the same are told apart by role. A
    `{field wording}` of `wordings` is handed the field's value, unless the name holds that field's value as well."""
    functions: List[PartFunction] = []
    taken = set()
    for part in parts:
        name = identifier(part.what, "part")
        if name in taken:
            name = f"{name}_{identifier(part.role, 'part')}"
        count = 2
        while name in taken:
            name, count = f"{name.rstrip('0123456789_')}_{count}", count + 1
        taken.add(name)
        slots = list(dict.fromkeys(identifier(slot, "value") for slot in _SLOT_NAME.findall(part.name)))
        worded = {slot: w for slot, w in (wordings or {}).items() if slot in slots and w.argument not in slots}
        functions.append(PartFunction(name, part, slots, worded,
                                      {slot: form for slot, form in (forms or {}).items() if slot in slots}))
    return functions


def props_module(parts: Iterable[Part], wordings: Optional[Dict[str, Wording]] = None,
                 forms: Optional[Dict[str, Form]] = None) -> str:
    """`src/api/parts.ts`: every part of the plan as a call whose result gives an element its role and its name."""
    return ("/** Generated from the page's plan: the role and the name each part of the page is read out by.\n"
            " *  Spread a part's call on the element that is that part. */\n\n"
            "type Value = string | number;\n\n"
            "/** A value as the plan words it; a value it words nowhere is shown as it is. */\n"
            "const worded = (wordings: Record<string, string>, value: Value): string =>\n"
            "  wordings[String(value)] ?? String(value);\n\n"
            "/** A whole number in `count` characters, zeros filled after its sign: 7 as \"007\", -3 as \"-03\". */\n"
            "const digits = (value: Value, count: number): string => {\n"
            "  const n = Math.trunc(Number(value));\n"
            "  return (n < 0 ? '-' : '') + String(Math.abs(n)).padStart(n < 0 ? count - 1 : count, '0');\n"
            "};\n\n"
            "/** A number with `count` digits after the point: 5 as \"5.00\". */\n"
            "const decimals = (value: Value, count: number): string => Number(value).toFixed(count);\n\n"
            "export const parts = {\n" + "".join(f.props() for f in part_functions(parts, wordings, forms)) + "};\n")


def locators_module(parts: Iterable[Part], wordings: Optional[Dict[str, Wording]] = None,
                    forms: Optional[Dict[str, Form]] = None) -> str:
    """`tests/e2e/parts.py`: every part of the plan as a function that returns its locator."""
    return ('"""The parts of the page, each found by the role and the whole name the page\'s plan gives it.\n\n'
            "Written by the engine from the plan (onboarding/page_parts.py); a change made here is overwritten.\n"
            '`page` is the page, or a locator to look inside.\n"""\n\n\n'
            "def _worded(wordings, value):\n"
            '    """A value as the plan words it."""\n'
            "    if str(value) not in wordings:\n"
            '        raise ValueError(f"{value!r} has no wording in the plan; it words {sorted(wordings)}")\n'
            "    return wordings[str(value)]\n\n\n"
            + _FORMS_PY +
            "def _in_states(**states):\n"
            '    """The states a part is looked for in: each one handed in; one left out may be either way."""\n'
            "    return {word: value for word, value in states.items() if value is not None}\n\n\n"
            + "\n\n".join(function.source() for function in part_functions(parts, wordings, forms)))


def locators_block(parts: Iterable[Part], shown: Optional[Dict[str, str]] = None,
                   wordings: Optional[Dict[str, Wording]] = None, forms: Optional[Dict[str, Form]] = None) -> str:
    """What a page test's writer is told of the functions, with how each shown value is written; empty when the
    plan names no part."""
    functions = part_functions(parts, wordings, forms)
    if not functions:
        return ""
    listed = "\n".join(f'- `{f.call()}`: {f.part.role} "{f.part.name}"' + _how_shown(f, shown or {})
                       for f in functions)
    return ("## The parts of the page\n`import parts` gives one function for each part the page's plan names by "
            "role and name. It returns the locator of that part, found by exactly that role and that whole name, "
            "with each value in braces handed in as the argument named after it, and a state the part is looked for in "
            "as true or false (left out, the part is found in either):\n\n" + listed + "\n\n"
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


def missing_parts(parts: Iterable[Part], sources: Iterable[str],
                  wordings: Optional[Dict[str, Wording]] = None) -> List[str]:
    """One defect for each part whose call no element of the page's files carries, named by the call as the writer
    was shown it (`wordings`: the plan's field wordings, so a worded slot is handed in as its field's value)."""
    source = "\n".join(sources)
    return [f'{MISSING}The plan names "{f.part.what}" ({f.part.role}, read out as "{f.part.name}") and no element '
            f'of the page carries `{f.spread()}`. Write the part as the plan describes it, with the step that '
            f'brings it up, and spread that call on its element in place of a role or a name of your own.'
            for f in part_functions(parts, wordings)
            if not re.search(r"\bparts\." + re.escape(f.page_name) + r"\s*\(", source)]
