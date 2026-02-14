# Continuous GDM Anchors Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace discrete GDM proposals with anchor-based guidance that lets the LLM output any continuous action (0.00–1.00), plus a soft validation log that does not override the action.

**Architecture:** In `StrategicAgent.gdm_module`, derive anchor actions around the last action (±0.2, clamped and de-duplicated). Simulate anchors, feed a prompt that explicitly allows any continuous value, parse the final action as before, then run a **soft** validation simulation for the chosen action and log the comparison in `llm_trace` (no action override). Update the decision prompt template to describe anchors as references.

**Tech Stack:** Python, `unittest`, existing `predict_future_trajectory`, prompt helpers.

---

### Task 1: Add failing test for continuous action prompt + soft validation log

**Files:**
- Modify: `tests/test_strategic_agent.py`

**Step 1: Write the failing test**

```python
def test_gdm_continuous_prompt_allows_free_action_and_logs_validation(self):
    from agents import strategic_agent

    agent = StrategicAgent(name="TestAgent", model_name="dummy-model", api_key="test")
    agent.current_opponent_model = {"alpha": 0.8, "beta": 0.1}
    agent.llm_trace = []

    def fake_call_llm(prompt, tag=None):
        agent.last_prompt = prompt
        return "[FINAL_ACTION] Action: 0.73"

    def fake_simulator(game_type, my_action, alpha, beta, num_players=2, steps=3):
        return {"total_reward": round(float(my_action), 3), "steps_detail": []}

    original_sim = strategic_agent.predict_future_trajectory
    strategic_agent.predict_future_trajectory = fake_simulator
    agent.call_llm = fake_call_llm

    try:
        action = agent.gdm_module(history=[[0.4, 0.4]], game_rules="Prisoner")
    finally:
        strategic_agent.predict_future_trajectory = original_sim

    self.assertEqual(action, 0.73)
    self.assertIn("Anchor 0.20", agent.last_prompt)
    self.assertIn("Anchor 0.40", agent.last_prompt)
    self.assertIn("Anchor 0.60", agent.last_prompt)
    self.assertIn("NOT limited", agent.last_prompt)
    self.assertTrue(any(e.get("tag") == "decision_validation" for e in agent.llm_trace))
```

**Step 2: Run test to verify it fails**

Run: `CONDA_OVERRIDE_CUDA=0 CONDA_NO_PLUGINS=true conda run -n rgrf python -m unittest tests/test_strategic_agent.py`  
Expected: FAIL (prompt lacks anchors/free-action wording and no validation trace).

---

### Task 2: Implement anchor-based GDM + soft validation trace

**Files:**
- Modify: `agents/strategic_agent.py`

**Step 1: Write minimal implementation**

- Replace `proposed_actions = [0.2, 0.5, 0.8]` with anchor generation around last action (±0.2, clamped, de-duplicated, ensure at least 3 anchors by adding 0.5 if needed).
- Format anchors with 2 decimals (e.g., `0.20`) for stable prompts.
- Simulate anchors and build `simulation_summary` lines like:  
  `Anchor 0.20 | Total 3-round Reward: 0.2 | Path: [...]`
- After parsing the LLM’s action, run `predict_future_trajectory` for the proposed action and compare it with the best anchor reward.  
  Append a soft validation entry to `agent.llm_trace`:
  ```python
  {
      "tag": "decision_validation",
      "model": "simulator",
      "prompt": "post-decision validation",
      "response": "chosen=0.73 best_anchor=0.60 chosen_reward=0.73 best_reward=0.60 delta=0.13"
  }
  ```
  (No action override.)

**Step 2: Run test to verify it passes**

Run: `CONDA_OVERRIDE_CUDA=0 CONDA_NO_PLUGINS=true conda run -n rgrf python -m unittest tests/test_strategic_agent.py`  
Expected: PASS.

**Step 3: Commit**

```bash
git add agents/strategic_agent.py tests/test_strategic_agent.py
git commit -m "feat: allow continuous GDM actions with anchor guidance"
```

---

### Task 3: Update decision prompt to emphasize continuous freedom

**Files:**
- Modify: `prompts/decision_prompt.py`

**Step 1: Write the failing test**

Extend the existing test in `tests/test_strategic_agent.py` to assert the new prompt contains the explicit freedom phrase (already in Task 1).

**Step 2: Implement prompt change**

- Add a clear instruction that anchors are references only.
- Include a line such as:  
  `You are NOT limited to these anchors; you may output ANY value in [0.00, 1.00].`

**Step 3: Run tests**

Run: `CONDA_OVERRIDE_CUDA=0 CONDA_NO_PLUGINS=true conda run -n rgrf python -m unittest tests/test_strategic_agent.py`  
Expected: PASS.

**Step 4: Commit**

```bash
git add prompts/decision_prompt.py
git commit -m "feat: clarify continuous action freedom in decision prompt"
```

---

### Task 4: Update logs and verify full test suite

**Files:**
- Modify: `ASSISTANT_CHANGELOG.md`
- Modify: `ASSISTANT_ISSUES.md` (only if new issues appear)

**Step 1: Update logs**

Record changes to continuous GDM anchors + soft validation in `ASSISTANT_CHANGELOG.md`.

**Step 2: Run full test suite**

Run: `CONDA_OVERRIDE_CUDA=0 CONDA_NO_PLUGINS=true conda run -n rgrf python -m unittest discover -s tests`  
Expected: PASS.

**Step 3: Commit**

```bash
git add ASSISTANT_CHANGELOG.md ASSISTANT_ISSUES.md
git commit -m "docs: log continuous GDM anchor update"
```

---

### Task 5: Merge to master (after tests pass)

**Step 1: Ensure no experiment logs are staged**

Check: `git status -sb`  
Confirm `results/experiment_CPD_20260210_175852.json` and `_trace.md` are NOT staged.

**Step 2: Merge into master**

```bash
cd /home/user/workplace/repos/rgrf
git checkout master
git merge reasoning-mode
```

**Step 3: Push (user confirms)**

```bash
git push -u origin master
```

