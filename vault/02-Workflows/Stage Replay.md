# Stage Replay

Finds where a cheaper model is good enough. A recorded run ([[Run Recorder]]) keeps each LLM call's stage, prompt, options and answer. `scripts/stage_replay.py` sends those exact prompts to other models, one stage at a time, so nothing upstream differs and any change in the answer comes from the model.

- Core: `backend/onboarding/stage_replay.py` (load calls, replay, score, summarise). Per-stage model choice uses `LLM_MODEL_<STAGE>`, which the replay sets only for the duration of the call.
- Score: well-formed by the recorded answer's own form (JSON parses, every `<<<marker>>>` present) and agreement with it (shared JSON leaves, or shared words). It measures closeness to the expensive answer, not correctness: the pipeline's gates (tests, build, QA) judge that.
- Sample each stage several times: one answer per model cannot tell a worse model from noise.
- A provider error is the run's error with no answer; nothing is retried or repaired.
