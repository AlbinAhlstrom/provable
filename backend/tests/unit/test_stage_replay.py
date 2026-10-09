"""Stage replay: a recorded LLM call is sent again to another model and its answer is scored against the recorded one."""
import json

from onboarding import stage_replay as sr


def _write(tmp_path, seq, stage, prompt, output, options=None, model="big", duration=10.0, tokens=100):
    entry = {"seq": seq, "step": f"llm.{stage}", "kind": "llm", "duration_s": duration,
             "input": {"stage": stage, "prompt": prompt, "options": options or {}}, "output": output,
             "meta": {"model": model, "completion_tokens": tokens}}
    (tmp_path / f"{seq:03d}_llm.{stage}.json").write_text(json.dumps(entry), encoding="utf-8")


def test_recorded_llm_calls_are_loaded_in_order_and_steps_are_skipped(tmp_path):
    """
    id: TST-REPLAY-001
    Given: A trace folder with two LLM calls and one deterministic step
    When: The calls are loaded
    Then: Only the LLM calls come back, in order, with stage, prompt, options, answer, model, time and tokens
    """
    _write(tmp_path, 2, "b", "pb", "ob", {"json_mode": True})
    _write(tmp_path, 1, "a", "pa", "oa", model="big", duration=4.5, tokens=7)
    (tmp_path / "003_step.json").write_text(json.dumps({"seq": 3, "kind": "step"}), encoding="utf-8")
    calls = sr.load_llm_calls(str(tmp_path))
    assert [c.stage for c in calls] == ["a", "b"]
    assert calls[0].prompt == "pa" and calls[0].output == "oa" and calls[0].model == "big"
    assert calls[0].duration_s == 4.5 and calls[0].completion_tokens == 7 and calls[1].options == {"json_mode": True}


def test_a_replay_sends_the_recorded_prompt_and_options_to_the_chosen_model_for_each_sample():
    """
    id: TST-REPLAY-002
    Given: A recorded call and a model double that records what it receives
    When: The call is replayed twice on a cheaper model
    Then: Two answers, each from the recorded prompt, stage and options, run with that model selected for the stage
    """
    import os
    seen = []

    def llm(prompt, stage="general", **options):
        seen.append((prompt, stage, options, os.environ.get("LLM_MODEL_" + stage.upper())))
        return "ok"

    call = sr.RecordedCall(seq=1, stage="ux_planning", prompt="P", options={"json_mode": True}, output="ref",
                           model="big", duration_s=9.0, completion_tokens=50)
    runs = sr.replay(call, "small", samples=2, llm=llm)
    assert [r.output for r in runs] == ["ok", "ok"] and all(r.error is None for r in runs)
    assert seen == [("P", "ux_planning", {"json_mode": True}, "small")] * 2
    assert os.environ.get("LLM_MODEL_UX_PLANNING") is None  # the choice does not outlive the replay


def test_an_empty_answer_is_an_error_carrying_the_providers_reason():
    """
    id: TST-REPLAY-003
    Given: A model that answers nothing and reports why
    When: The call is replayed
    Then: The run carries that reason and no answer, never a made-up one
    """
    call = sr.RecordedCall(1, "s", "P", {}, "ref", "big", 1.0, 1)
    runs = sr.replay(call, "small", samples=1, llm=lambda p, stage="g", **o: "", error_of=lambda: "quota")
    assert runs[0].output == "" and runs[0].error == "quota"


def test_json_answers_are_scored_by_validity_and_agreement_with_the_reference():
    """
    id: TST-REPLAY-004
    Given: A JSON reference, an identical answer, one that differs in a value, one missing a key, and broken JSON
    When: Each is scored
    Then: Identical scores 1.0; the others score lower in that order; broken JSON is invalid with 0
    """
    ref = json.dumps({"a": 1, "b": {"c": "x", "d": [1, 2]}})
    same = sr.score(ref, ref)
    value = sr.score(ref, json.dumps({"a": 1, "b": {"c": "y", "d": [1, 2]}}))
    missing = sr.score(ref, json.dumps({"a": 1}))
    broken = sr.score(ref, '{"a": 1,}')
    assert same.valid and same.agreement == 1.0
    assert value.valid and missing.valid and 0 < missing.agreement < value.agreement < 1.0
    assert not broken.valid and broken.agreement == 0.0


def test_marked_file_answers_must_keep_every_marker_of_the_reference():
    """
    id: TST-REPLAY-005
    Given: A reference answer of marker-delimited files
    When: An answer lacking the end marker and one with all markers are scored
    Then: The first is invalid; the second is valid
    """
    ref = "<<<view_tsx>>>\ncode a\n<<<app_tsx>>>\ncode b\n<<<end>>>"
    assert not sr.score(ref, "<<<view_tsx>>>\ncode a\n<<<app_tsx>>>\ncode b").valid
    assert sr.score(ref, "<<<view_tsx>>>\ncode a2\n<<<app_tsx>>>\ncode b\n<<<end>>>").valid


def test_prose_answers_are_scored_by_shared_words_and_an_empty_answer_is_invalid():
    """
    id: TST-REPLAY-006
    Given: A prose reference
    When: A near copy, an unrelated text and an empty answer are scored
    Then: The copy agrees more than the unrelated text; the empty answer is invalid
    """
    ref = "the quick brown fox jumps over the lazy dog"
    assert sr.score(ref, "the quick brown fox leaps over the lazy dog").agreement > sr.score(ref, "alpha beta gamma").agreement
    assert not sr.score(ref, "").valid


def test_a_stage_summary_compares_a_model_with_the_recorded_run():
    """
    id: TST-REPLAY-007
    Given: A recorded call (10 s, 100 tokens) and three replays on a cheaper model, one of them invalid
    When: The stage is summarised
    Then: Validity rate, mean agreement over the valid ones, and the speed-up against the recording are reported
    """
    call = sr.RecordedCall(1, "s", "P", {}, json.dumps({"a": 1}), "big", 10.0, 100)
    runs = [sr.Run(json.dumps({"a": 1}), 2.0, 10, None), sr.Run(json.dumps({"a": 2}), 4.0, 10, None),
            sr.Run("{bad", 3.0, 10, None)]
    s = sr.summarise(call, "small", runs)
    assert s.stage == "s" and s.model == "small" and s.samples == 3
    assert abs(s.valid_rate - 2 / 3) < 1e-9 and abs(s.mean_agreement - 0.5) < 1e-9
    assert abs(s.mean_duration_s - 3.0) < 1e-9 and abs(s.speedup - 10.0 / 3.0) < 1e-9
