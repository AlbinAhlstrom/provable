"""One LLM call through Anthropic's own Messages API.

Its OpenAI-compatible endpoint ignores `reasoning_effort` and `response_format`, so the effort setting and a stage's
answer schema reach the model only this way. The caller (agent_orchestrator.call_gemini) owns keys, errors and tracing.
"""

import base64
import threading
from typing import Any, Dict, List, Optional, Tuple

from anthropic import Anthropic, transform_schema

# The most one answer may hold, hidden thinking included: the model's own maximum, so a call is bounded by its
# timeout and never cut short here (at 32,000 a page's thinking alone used the room and no page was written).
MAX_OUTPUT_TOKENS = 128000

# The provider refuses requests beyond a number in flight for the whole account (a 429; some thirty side-by-side
# calls of one kickstart lost four that way), so calls wait their turn here. Waiting is not a retry: each call is
# still sent once.
MAX_CONCURRENT_REQUESTS = 12
_in_flight = threading.BoundedSemaphore(MAX_CONCURRENT_REQUESTS)


def _content(prompt: str, images: Optional[List[str]]) -> Any:
    """The user message: the prompt alone, or the prompt followed by each image as a base64 block."""
    if not images:
        return prompt
    parts: List[Dict[str, Any]] = [{"type": "text", "text": prompt}]
    for path in images:
        with open(path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("ascii")
        parts.append({"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": encoded}})
    return parts


def _usage_meta(usage: Any) -> Dict[str, Optional[int]]:
    """Token counts in the trace's form. This API reports cached input beside the uncached input, so the prompt is
    their sum; hidden thinking is billed inside the output tokens and not reported apart."""
    cached = getattr(usage, "cache_read_input_tokens", None) or 0
    prompt = (getattr(usage, "input_tokens", None) or 0) + cached + (getattr(usage, "cache_creation_input_tokens", None) or 0)
    completion = getattr(usage, "output_tokens", None) or 0
    return {"prompt_tokens": prompt, "completion_tokens": completion, "total_tokens": prompt + completion,
            "reasoning_tokens": None, "cached_tokens": cached}


def complete(api_key: str, model: str, prompt: str, images: Optional[List[str]], effort: str,
             json_schema: Optional[Dict[str, Any]], timeout_s: float,
             thinking: bool = True) -> Tuple[str, Dict[str, Optional[int]], str]:
    """Sends one prompt and returns the answer's text, its token counts and why the model stopped. `thinking=False`
    asks for the answer without hidden thinking; otherwise the model's own default holds."""
    output_config: Dict[str, Any] = {"effort": effort} if effort else {}
    if json_schema:
        output_config["format"] = {"type": "json_schema", "schema": transform_schema(json_schema)}
    client = Anthropic(api_key=api_key, max_retries=0)
    with _in_flight:
        response = client.messages.create(
            model=model, max_tokens=MAX_OUTPUT_TOKENS, timeout=timeout_s,
            messages=[{"role": "user", "content": _content(prompt, images)}],
            **({"output_config": output_config} if output_config else {}),
            **({} if thinking else {"thinking": {"type": "disabled"}}))
    text = "".join(block.text for block in response.content if block.type == "text")
    return text, _usage_meta(response.usage), response.stop_reason
