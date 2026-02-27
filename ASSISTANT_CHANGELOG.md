# Assistant Change Log
## 2026-02-09
- Added unit tests for OpenRouter base URL normalization and header injection.
- Added unit test to ensure `StrategicAgent.gdm_module` runs without a simulator signature error.
- Normalized LLM base URLs (e.g., stripping `/chat/completions`) and added optional OpenRouter headers from environment variables in `LLMConnector`.
- Fixed `StrategicAgent` simulator call to use correct argument names/order for `predict_future_trajectory`.
- Added env-based API key/config helpers in `main_experiment.py` and removed hard-coded keys.
- Added tests for env-based config loading in `main_experiment.py`.
- Added `.env` loading via `python-dotenv` and support for multi-player JSON configs in `RGRF_PLAYER_CONFIGS_JSON`.
- Added `requirements.txt` with core Python dependencies.
- Added a `.env` sample file with placeholders and optional multi-player config.
- Fixed `calculate_advanced_metrics` stability assignment for short runs.
- Sanitized saved results to remove API keys from metadata and added sanitizer in code.
- Moved advanced metrics computation into `run_experiment` and restored 2-value return.
- Added unit tests for metrics stability and API key redaction.
- Redacted API keys from existing `results/experiment_*.json` files.
- Added Markdown trace logging per round with prompt/response capture.
- Added LLM call tracing in `BaseAgent` and tagged calls across agents/modules.
- Added unit test to ensure `_trace.md` logs are generated.
- Added design doc for LLM trace logging.

### Tests
- `CONDA_OVERRIDE_CUDA=0 CONDA_NO_PLUGINS=true conda run -n rgrf python -m unittest discover -s tests`

### Tests
- `CONDA_OVERRIDE_CUDA=0 CONDA_NO_PLUGINS=true conda run -n rgrf python -m unittest tests/test_strategic_agent.py`
- `CONDA_OVERRIDE_CUDA=0 CONDA_NO_PLUGINS=true conda run -n rgrf python -m unittest tests/test_reflection_prompt.py`

## 2026-02-10
- Initialized git repository and added `.gitignore` for Python caches and `.env`.
- Added history window support in `BaseAgent` and applied windowing in all LLM agents (ZeroShot/CoT/ReAct/Strategic).
- Added history window unit tests for `clip_history` and prompt windowing.
- Added design doc for history window feature.

### Tests
- `python -m unittest tests/test_history_window.py`

## 2026-02-10
- Added reasoning-mode prompt helper controlled by `RGRF_REASONING_MODE`.
- Added concise game context helper and injected game context into Strategic prompts.
- Added/updated tests for reasoning mode and game context helpers.

### Tests
- `python -m unittest tests/test_reasoning_mode.py`
- `python -m unittest tests/test_game_context.py`

## 2026-02-10
- Synced `storage/notes.txt` from worktree run output.

## 2026-02-14
- Replaced GDM discrete proposals with anchor-based guidance for continuous actions.
- Added soft post-decision validation trace entry (no action override).
- Updated decision prompt to emphasize anchors as references and allow any 0–1 value.
- Added unit test for continuous-action prompt and validation logging.

### Tests
- `CONDA_OVERRIDE_CUDA=0 CONDA_NO_PLUGINS=true conda run -n rgrf python -m unittest discover -s tests`

## 2026-02-22
- Process note: work on a new worktree branch, test in that branch, and only merge to master after user approval.
- Clarified CPD action semantics in game context and added a reminder in strategic reflection prompt.


## 2026-02-22
- Relaxed StrategicAgent parsing to accept escaped `[FINAL_ACTION]` tags and `[FINAL_NOTE]` without `Note:`.
- Added unit tests for escaped action parsing and missing-note-prefix extraction.
- Added `RGRF_DECISION_VALIDATION` toggle to gate post-decision validation (extra simulator call + trace entry).
- Added unit test for decision validation toggle behavior.
- Clarified reflection prompt to surface Avg_Others and forbid including self-action in averages.
- Added unit test for Avg_Others-only instruction in reflection prompt.

## 2026-02-27
- Clarified counterfactual handling in strategic reflection prompt with explicit clamp to [0, 1].
- Clarified anchor role in decision prompt to emphasize trend-first selection and required a brief rationale when diverging.
- Added unit tests for counterfactual clamp instruction and decision prompt anchor guidance.
- Emphasized belief/correction output format requirements and made model parsing more tolerant to loose alpha/beta formats.
- Added unit tests for belief prompt emphasis, correction prompt emphasis, and tolerant alpha/beta parsing.

### Tests
- `CONDA_OVERRIDE_CUDA=0 CONDA_NO_PLUGINS=true conda run -n rgrf python -m unittest tests/test_reflection_prompt.py tests/test_decision_prompt.py`
- `CONDA_OVERRIDE_CUDA=0 CONDA_NO_PLUGINS=true conda run -n rgrf python -m unittest tests/test_belief_prompt.py tests/test_amm_cvm.py`
