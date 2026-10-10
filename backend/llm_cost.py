"""What an LLM call costs: the tokens a provider reported, priced per model, in USD and SEK.

Prices are list prices in USD per million tokens (artificialanalysis.ai, read 2026-10-09). A model the table does not
hold has no price: its cost is None and the run names it as unpriced, so a missing price never reads as a cheap run.
A model id is matched by its longest known prefix, so a dated or preview variant takes the price of its family.
PROVABLE_USD_SEK sets the exchange rate; every summary stores the rate it was priced at.
"""

import os
from dataclasses import dataclass
from typing import Any, Dict, Optional

PRICES_AS_OF = "2026-10-09"
DEFAULT_USD_SEK = 10.0  # 10.007 on 2026-10-08


@dataclass(frozen=True)
class ModelPrice:
    """USD per million tokens."""
    input: float
    output: float
    cached_input: float


PRICES: Dict[str, ModelPrice] = {
    "gemini-3.8-flash": ModelPrice(input=0.75, output=3.75, cached_input=0.075),
    "gemini-3.5-flash-lite": ModelPrice(input=0.30, output=2.50, cached_input=0.03),
    "gpt-6-luna": ModelPrice(input=0.10, output=0.50, cached_input=0.01),
    "gpt-6.1-sol": ModelPrice(input=2.00, output=10.00, cached_input=0.10),
    "claude-haiku-5-5": ModelPrice(input=0.10, output=0.50, cached_input=0.01),
    "claude-opus-5-5": ModelPrice(input=4.00, output=20.00, cached_input=0.40),
    "mimo-v2.6-flash": ModelPrice(input=0.14, output=0.28, cached_input=0.0028),
    "mimo-v2.6-pro": ModelPrice(input=0.43, output=0.87, cached_input=0.0043),
    "deepseek-v4.1-flash": ModelPrice(input=0.30, output=1.20, cached_input=0.006),
}


def usd_to_sek() -> float:
    return float(os.environ.get("PROVABLE_USD_SEK") or DEFAULT_USD_SEK)


def price_for(model: Optional[str]) -> Optional[ModelPrice]:
    name = (model or "").lower().split("/")[-1]  # a router prefixes the vendor: "google/gemini-3.8-flash"
    known = [key for key in PRICES if name.startswith(key)]
    return PRICES[max(known, key=len)] if known else None


def call_cost_usd(meta: Dict[str, Any]) -> Optional[float]:
    """The cost of one traced LLM call from its `meta`, or None when its model has no price. Hidden reasoning is billed
    as output: providers report it either inside the completion or only in the total, so the larger reading counts."""
    price = price_for(meta.get("model"))
    if price is None:
        return None
    prompt = meta.get("prompt_tokens") or 0
    cached = min(meta.get("cached_tokens") or 0, prompt)
    output = max(meta.get("completion_tokens") or 0, (meta.get("total_tokens") or 0) - prompt)
    return ((prompt - cached) * price.input + cached * price.cached_input + output * price.output) / 1_000_000
