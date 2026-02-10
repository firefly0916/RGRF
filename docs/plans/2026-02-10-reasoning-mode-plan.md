# Reasoning Mode + Game Context Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a global reasoning-mode toggle that requests brief thinking + final outputs for all LLM prompts, and inject concise game context into Strategic module prompts, while preserving existing `[FINAL_*]` parsing.

**Architecture:** Introduce a `reasoning_mode` flag in `BaseAgent` sourced from `RGRF_REASONING_MODE`. Provide helpers in `prompts/` for reasoning instructions and game context. Update all LLM prompts to include reasoning instructions; update Strategic prompts to include game context. Keep metrics global and parsing unchanged.

**Tech Stack:** Python (stdlib), existing prompt helpers, `unittest`.

---

### Task 1: Add a helper for reasoning instructions

**Files:**
- Create: `prompts/reasoning_prompt.py`
- Test: `tests/test_reasoning_mode.py`

**Step 1: Write the failing test**

```python
import os
import unittest

import prompts.reasoning_prompt as rp


class TestReasoningPrompt(unittest.TestCase):
    def test_reasoning_instructions_on(self):
        os.environ["RGRF_REASONING_MODE"] = "1"
        self.assertIn("Reasoning", rp.reasoning_instructions())
        self.assertIn("FINAL", rp.reasoning_instructions())

    def test_reasoning_instructions_off(self):
        os.environ["RGRF_REASONING_MODE"] = "0"
        self.assertEqual("", rp.reasoning_instructions())


if __name__ == "__main__":
    unittest.main()
```

**Step 2: Run test to verify it fails**

Run: `python -m unittest tests/test_reasoning_mode.py`
Expected: FAIL (module not found or function missing)

**Step 3: Write minimal implementation**

```python
# prompts/reasoning_prompt.py
import os


def reasoning_instructions():
    enabled = os.getenv("RGRF_REASONING_MODE", "0")
    if str(enabled).strip().lower() in ("1", "true", "yes", "on"):
        return "\n[Reasoning]\nProvide brief reasoning (<=4 sentences), then give the required [FINAL_*] line.\n"
    return ""
```

**Step 4: Run test to verify it passes**

Run: `python -m unittest tests/test_reasoning_mode.py`
Expected: PASS

**Step 5: Commit**

```bash
git add prompts/reasoning_prompt.py tests/test_reasoning_mode.py
git commit -m "feat: add reasoning prompt helper"
```

---

### Task 2: Add concise game context helper for Strategic prompts

**Files:**
- Create: `prompts/game_context.py`
- Test: `tests/test_game_context.py`

**Step 1: Write the failing test**

```python
import unittest

import prompts.game_context as gc


class TestGameContext(unittest.TestCase):
    def test_cpd_context_contains_formula(self):
        text = gc.get_game_context("CPD")
        self.assertIn("Prisoner's Dilemma", text)
        self.assertIn("Reward =", text)

    def test_pgg_context_contains_formula(self):
        text = gc.get_game_context("PGG")
        self.assertIn("Public Goods", text)
        self.assertIn("reward", text.lower())

    def test_unknown_context_empty(self):
        self.assertEqual("", gc.get_game_context("OTHER"))


if __name__ == "__main__":
    unittest.main()
```

**Step 2: Run test to verify it fails**

Run: `python -m unittest tests/test_game_context.py`
Expected: FAIL (module not found or function missing)

**Step 3: Write minimal implementation**

```python
# prompts/game_context.py

def get_game_context(game_type):
    if game_type == "CPD":
        return "[Game Context]\nGame: Continuous Prisoner's Dilemma\nReward = (1.5 * Average_of_Others_Actions) - Your_Action\nAction range: 0 to 1\n"
    if game_type == "PGG":
        return "[Game Context]\nGame: Public Goods Game\nReward = (Total_Pool * 2.0 / Total_Players) + (1.0 - Your_Contribution)\nAction range: 0 to 1\n"
    return ""
```

**Step 4: Run test to verify it passes**

Run: `python -m unittest tests/test_game_context.py`
Expected: PASS

**Step 5: Commit**

```bash
git add prompts/game_context.py tests/test_game_context.py
git commit -m "feat: add game context helper"
```

---

### Task 3: Apply reasoning instructions to all LLM prompts

**Files:**
- Modify: `agents/zero_shot_agent.py`
- Modify: `agents/cot_agent.py`
- Modify: `agents/react_agent.py`
- Modify: `prompts/belief_prompt.py`
- Modify: `prompts/decision_prompt.py`
- Modify: `prompts/reflection_prompt.py`
- Test: `tests/test_reasoning_mode.py`

**Step 1: Write the failing test**

```python
import os
import unittest

from agents.zero_shot_agent import ZeroShotAgent


class RecordingZeroShot(ZeroShotAgent):
    def __init__(self):
        self.last_prompt = None

    def call_llm(self, prompt, tag=None):
        self.last_prompt = prompt
        return "[FINAL_ACTION] Action: 0.5"


class TestReasoningModePrompt(unittest.TestCase):
    def test_reasoning_prompt_included(self):
        os.environ["RGRF_REASONING_MODE"] = "1"
        agent = RecordingZeroShot()
        agent.get_action(history=[], game_rules="RULES")
        self.assertIn("[Reasoning]", agent.last_prompt)


if __name__ == "__main__":
    unittest.main()
```

**Step 2: Run test to verify it fails**

Run: `python -m unittest tests/test_reasoning_mode.py`
Expected: FAIL (no reasoning instructions in prompt)

**Step 3: Write minimal implementation**

- Add `reasoning_instructions()` to each prompt template via `prompts.reasoning_prompt`.
- Ensure `[FINAL_*]` instructions remain unchanged.

**Step 4: Run test to verify it passes**

Run: `python -m unittest tests/test_reasoning_mode.py`
Expected: PASS

**Step 5: Commit**

```bash
git add agents/zero_shot_agent.py agents/cot_agent.py agents/react_agent.py prompts/belief_prompt.py prompts/decision_prompt.py prompts/reflection_prompt.py tests/test_reasoning_mode.py
git commit -m "feat: add reasoning mode to prompts"
```

---

### Task 4: Inject game context into Strategic module prompts

**Files:**
- Modify: `agents/strategic_agent.py`
- Modify: `modules/amm_cvm.py`
- Modify: `prompts/belief_prompt.py`
- Modify: `prompts/decision_prompt.py`
- Modify: `prompts/reflection_prompt.py`
- Test: `tests/test_game_context.py`

**Step 1: Write the failing test**

```python
import unittest

from prompts.belief_prompt import get_belief_template


class TestStrategicGameContext(unittest.TestCase):
    def test_belief_prompt_includes_context(self):
        text = get_belief_template("hist", "notes", "results", "CTX")
        self.assertIn("Game Context", text)


if __name__ == "__main__":
    unittest.main()
```

**Step 2: Run test to verify it fails**

Run: `python -m unittest tests/test_game_context.py`
Expected: FAIL (signature mismatch or missing context)

**Step 3: Write minimal implementation**

- Extend prompt helper signatures to accept `game_context` string (append into prompt near top).
- Update Strategic call sites in `amm_cvm.py` and `StrategicAgent.gdm_module` + `reflect` to pass game_context from `game_rules` via `prompts.game_context.get_game_context()`.

**Step 4: Run test to verify it passes**

Run: `python -m unittest tests/test_game_context.py`
Expected: PASS

**Step 5: Commit**

```bash
git add agents/strategic_agent.py modules/amm_cvm.py prompts/belief_prompt.py prompts/decision_prompt.py prompts/reflection_prompt.py tests/test_game_context.py
git commit -m "feat: inject game context into strategic prompts"
```

---

### Task 5: Update logs

**Files:**
- Modify: `ASSISTANT_CHANGELOG.md`
- Modify: `ASSISTANT_ISSUES.md` (only if new issues observed)

**Step 1: Append change log**

```
## 2026-02-10
- Added global reasoning-mode prompt instructions controlled by `RGRF_REASONING_MODE`.
- Added concise game context injection into Strategic prompts.
- Added tests for reasoning mode and game context helpers.
```

**Step 2: Commit**

```bash
git add ASSISTANT_CHANGELOG.md
git commit -m "docs: log reasoning mode and game context changes"
```
```
