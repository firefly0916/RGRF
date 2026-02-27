# Assistant Issues Log

## 2026-02-27
- Issue: `CONDA_OVERRIDE_CUDA=0 CONDA_NO_PLUGINS=true conda run -n rgrf python main_experiment.py` in `soft-constraint-prompts` produced no output after ~10s; process terminated (no stdout observed).
  Status: investigated. Capturing stdout to file with `PYTHONUNBUFFERED=1` showed the run progressed but all LLM calls failed with `Connection error` to `openai/gpt-4o` (likely network/API access in Codex environment). Output not appearing is consistent with buffering/capture; the run is not stuck.
- Issue: Strategic agent shows over-cooperation in later rounds versus zero_shot, leading to low/negative payoffs.
  Status: noted for later tuning.
- Issue: Opponent model (alpha/beta) oscillates across rounds, causing unstable decision anchors.
  Status: noted for later tuning.
- Issue: Belief/reflection should clamp predicted opponent actions to [0, 1] to avoid negative expected values.
  Status: noted for later tuning.

## 2026-02-22
- Issue: `conda run -n rgrf python main_experiment.py` in `soft-constraint-prompts` produced no output after ~80s; terminated manually; no new `results/experiment_*` files created.
  Status: unresolved (likely waiting on first LLM call or blocked before first print).

## 2026-02-09
- Issue: conda commands failed without `CONDA_OVERRIDE_CUDA=0 CONDA_NO_PLUGINS=true` (permission/plugin errors).
  Status: mitigated by using those env vars for conda commands.
- Issue: conda install failed due to DNS resolution for `repo.anaconda.com` and an unrecognized `libmamba` solver.
  Status: user installed `numpy` manually in `rgrf` environment.
- Issue: conda install failed with `NoWritablePkgsDirError` for `/home/user/miniconda3/pkgs` and `/home/user/.conda/pkgs`.
  Status: user installed `numpy` manually in `rgrf` environment.
- Issue: `predict_future_trajectory()` called with wrong parameters in `StrategicAgent.gdm_module`.
  Status: fixed in `agents/strategic_agent.py`.
- Issue: OpenRouter base_url used `/chat/completions` (incompatible with OpenAI client base_url).
  Status: fixed in `llm/connector.py` via base_url normalization.
- Issue: `main_experiment.py` run failed because no API key in environment.
  Status: resolved. API key now supplied via `.env`.
- Issue: One-round run failed again after `.env` support because API key still missing.
  Status: resolved. API key now supplied via `.env`.
- Issue: One-round run appeared to hang during LLM call; no output after several seconds.
  Status: mitigated. Subsequent run completed; may still be intermittent network/API latency.
- Issue: One-round run completed but LLM calls failed with repeated "Connection error" for `openai/gpt-4o`.
  Status: mitigated. Subsequent local run succeeded; may still be intermittent network/API issue.
- Issue: `python main_experiment.py` run hung with no output; interrupted after ~50s.
  Status: unresolved. Likely waiting on LLM response before first print; may require timeout/health check or smaller rounds.
- Issue: `main_experiment.py` has a NameError risk in `calculate_advanced_metrics` when rounds < 2 (uses `稳定性` instead of `stability`).
  Status: resolved. Fixed variable name and added test.
- Issue: `main_experiment.py` references undefined `result_data` after `run_experiment`, which will raise `NameError`.
  Status: resolved. Removed undefined reference and moved metrics into `run_experiment`.
- Issue: `results/*.json` currently store raw API keys in `metadata.player_configs`.
  Status: resolved. Added sanitizer and redacted existing files.

## 2026-02-10
- Issue: `git push` to GitHub via SSH failed (DNS/port 22 connection closed).
  Status: unresolved. May require HTTPS remote or SSH key/network access.
- Update: `ssh -T git@github.com` failed with DNS resolution error on this machine; SSH push still fails.
  Status: unresolved (likely DNS/network blocking github.com).

## 2026-02-10
- Issue: `python -m unittest discover -s tests` failed in worktree due to missing dependencies (`openai`, `python-dotenv`, `numpy`).
  Status: unresolved (install deps or run in configured env).
- Update: Running tests inside `conda run -n rgrf` succeeds; dependency-related test failures resolved.
  Status: resolved.
- Issue: `conda run -n rgrf python main_experiment.py` produced no output for ~10s; interrupted.
  Status: unresolved (may be waiting on LLM or blocked before first print).
- Update: `conda run -n rgrf python main_experiment.py` still produced no output after ~120s; interrupted.
  Status: unresolved (likely blocked before first print or waiting on LLM).
- Update: `git push` from master failed again due to DNS resolution for github.com.
  Status: unresolved on this environment; push may require user-side network.
