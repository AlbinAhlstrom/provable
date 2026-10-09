"""A prompt names kinds of things, never the vocabulary of the one product somebody was debugging."""

import glob
import os
import re

import pytest

PROMPTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "prompts"))

# Words that belong to one product. An example in a prompt speaks of categories (a game, an order, a booking, a
# grid, a party, a status); these are the words a prompt picks up when it is tuned on a single pitch.
ONE_PRODUCT_WORDS = [
    r"chess", r"pawns?", r"knights?", r"bishops?", r"rooks?", r"checkmate", r"castling", r"tic-?tac-?toe",
    r"boards?", r"squares?", r"pieces",
    r"pizzas?", r"salons?", r"hair", r"babysitt\w*", r"sitting", r"child profile", r"family profile", r"kitchen",
    r"hotels?", r"pallets?",
]
ONE_PRODUCT = re.compile(r"\b(" + "|".join(ONE_PRODUCT_WORDS) + r")\b|[♔-♟]", re.IGNORECASE)


def _prompt_files():
    return sorted(glob.glob(os.path.join(PROMPTS_DIR, "*.md")))


def test_there_are_prompts_to_check():
    assert _prompt_files()


@pytest.mark.parametrize("path", _prompt_files(), ids=os.path.basename)
def test_a_prompt_holds_no_word_of_a_single_product(path):
    """Verify no prompt is tuned on one pitch.

    id: TST-PROMPT-NEUTRAL-001
    Given: A prompt the pipeline sends to a model
    When: Its text is read
    Then: It holds no word that belongs to one product (a chess term, a babysitter's term, a chess glyph)
    """
    with open(path, encoding="utf-8") as handle:
        lines = handle.read().split("\n")
    found = [f"line {number}: '{match.group(0)}'" for number, line in enumerate(lines, 1)
             for match in ONE_PRODUCT.finditer(line)]
    assert not found, (f"{os.path.basename(path)} speaks one product's language ({'; '.join(found)}). "
                       "Say it in terms of the contract (owners, kinds, statuses, positions), with examples from "
                       "at least two unrelated kinds of product. See .claude/rules/pipeline.md, 'Prompts are domain-neutral'.")
