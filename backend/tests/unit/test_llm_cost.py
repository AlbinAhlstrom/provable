"""Unit tests for what an LLM call costs (backend/llm_cost.py) and for the cost a recorded run carries."""

import json

import pytest

import llm_cost
import pipeline_trace
import run_recorder
from pipeline_trace import traced_llm

FLASH = "gemini-3.8-flash"  # 0.75 USD in, 0.075 cached in, 3.75 out, per million tokens


def test_a_call_is_priced_from_its_fresh_cached_and_output_tokens():
    """Verify the three token kinds are each billed at their own rate.

    id: TST-COST-001
    Given: A call with 1,000,000 prompt tokens of which 400,000 were cache hits, and 100,000 answer tokens
    When: The call is priced
    Then: It costs 0.6 x 0.75 + 0.4 x 0.075 + 0.1 x 3.75 = 0.855 USD
    """
    meta = {"model": FLASH, "prompt_tokens": 1_000_000, "cached_tokens": 400_000, "completion_tokens": 100_000,
            "total_tokens": 1_100_000}
    assert llm_cost.call_cost_usd(meta) == pytest.approx(0.855)


def test_hidden_reasoning_is_billed_as_output():
    """Verify thinking tokens the provider reports on top of the answer are paid for.

    id: TST-COST-002
    Given: A call whose total holds 80 tokens beyond the prompt and the visible answer
    When: The call is priced
    Then: 110 output tokens are billed, not 30
    """
    meta = {"model": FLASH, "prompt_tokens": 10, "completion_tokens": 30, "total_tokens": 120, "reasoning_tokens": 80}
    assert llm_cost.call_cost_usd(meta) == pytest.approx((10 * 0.75 + 110 * 3.75) / 1_000_000)


def test_a_dated_model_id_takes_the_price_of_its_family_and_an_unknown_model_has_no_price():
    """Verify an unknown model is reported as unpriced instead of being counted as free.

    id: TST-COST-003
    Given: A dated variant of a priced model, and a model the table does not hold
    When: Each is looked up
    Then: The variant has its family's price and the unknown one has none
    """
    assert llm_cost.price_for(FLASH + "-preview-09-2026") == llm_cost.price_for(FLASH)
    assert llm_cost.price_for("some-model-nobody-priced") is None
    assert llm_cost.call_cost_usd({"model": "some-model-nobody-priced", "prompt_tokens": 5}) is None


@traced_llm
def _llm(prompt, stage="general", model=FLASH):
    pipeline_trace.record_llm_meta(model=model, prompt_tokens=1_000_000, completion_tokens=100_000,
                                   total_tokens=1_100_000, cached_tokens=400_000)
    return "answer"


@pytest.fixture
def runs_root(monkeypatch, tmp_path):
    root = tmp_path / "runs"
    monkeypatch.setenv("PROVABLE_RUNS_DIR", str(root))
    monkeypatch.setenv("PROVABLE_USD_SEK", "10")
    monkeypatch.delenv("PROVABLE_RECORD_RUNS", raising=False)
    monkeypatch.delenv("PROVABLE_TRACE_DIR", raising=False)
    return root


def _summary(root):
    (run,) = [p for p in root.iterdir() if p.is_dir()]
    return run, json.loads((run / "summary.json").read_text(encoding="utf-8"))


def test_a_run_records_what_it_cost_in_sek_per_stage_and_in_total(runs_root):
    """Verify the summary of a run carries its real cost.

    id: TST-COST-004
    Given: A run with two priced calls in different stages, at 10 SEK to the dollar
    When: The run ends
    Then: The summary holds cached tokens, the cost per stage and in total in USD and SEK, and the rate used
    """
    with run_recorder.recorded_run("kickstart", "p"):
        _llm("a", stage="writer")
        _llm("b", stage="reviewer")
    _, summary = _summary(runs_root)
    llm = summary["llm"]
    assert llm["cached_tokens"] == 800_000
    assert llm["cost_usd"] == pytest.approx(1.71) and llm["cost_sek"] == pytest.approx(17.1)
    assert llm["usd_to_sek"] == 10 and llm["unpriced_models"] == []
    assert llm["by_stage"]["writer"]["cost_sek"] == pytest.approx(8.55)


def test_a_run_on_an_unpriced_model_names_it_and_claims_no_total(runs_root):
    """Verify a cost that cannot be known is not shown as a smaller one.

    id: TST-COST-005
    Given: A run with one priced call and one call on a model without a price
    When: The run ends
    Then: The summary names the unpriced model and its total cost is empty
    """
    with run_recorder.recorded_run("kickstart", "p"):
        _llm("a", stage="writer")
        _llm("b", stage="reviewer", model="some-model-nobody-priced")
    llm = _summary(runs_root)[1]["llm"]
    assert llm["unpriced_models"] == ["some-model-nobody-priced"]
    assert llm["cost_sek"] is None and llm["by_stage"]["writer"]["cost_sek"] == pytest.approx(8.55)


def test_an_older_run_gets_its_cost_from_its_trace(runs_root):
    """Verify runs recorded before costs existed can be priced afterwards.

    id: TST-COST-006
    Given: A finished run whose summary holds no cost
    When: The runs are backfilled
    Then: Its summary holds the cost its trace adds up to, and the rest of the summary is untouched
    """
    with run_recorder.recorded_run("kickstart", "p"):
        _llm("a", stage="writer")
    run, summary = _summary(runs_root)
    summary["llm"] = {"calls": 1, "prompt_tokens": 1_000_000}
    (run / "summary.json").write_text(json.dumps(summary), encoding="utf-8")

    assert run_recorder.backfill_costs() == [run.name]
    after = _summary(runs_root)[1]
    assert after["llm"]["cost_sek"] == pytest.approx(8.55)
    assert after["status"] == summary["status"] and after["stages"] == summary["stages"]
