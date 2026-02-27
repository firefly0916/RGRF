# Strategic Prompt Rule Clarification Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Clarify CPD action semantics (higher action = more cooperation) in strategic prompts and add tests to prevent regression.

**Architecture:** Add one sentence to CPD game context and a short semantics reminder in the reflection prompt. Keep output formats unchanged. Validate via unit tests on prompt text.

**Tech Stack:** Python 3.10, unittest.

---

### Task 1: Add failing tests for CPD semantics in prompts

**Files:**
- Modify: `tests/test_game_context.py`
- Create: `tests/test_reflection_prompt.py`

**Step 1: Write the failing test (game context)**

```python
    def test_cpd_context_mentions_cooperation_semantics(self):
        text = gc.get_game_context("CPD")
        self.assertIn("higher action = more cooperation", text.lower())
```

**Step 2: Write the failing test (reflection prompt)**

```python
import unittest
from prompts.reflection_prompt import get_reflection_template


class TestReflectionPrompt(unittest.TestCase):
    def test_reflection_prompt_mentions_action_semantics(self):
        text = get_reflection_template(0.5, 0.5, 0.5, 1.0, 0.0, "CTX")
        self.assertIn("higher action = more cooperation", text.lower())


if __name__ == "__main__":
    unittest.main()
```

**Step 3: Run tests to verify they fail**

Run: `CONDA_OVERRIDE_CUDA=0 CONDA_NO_PLUGINS=true conda run -n rgrf python -m unittest tests/test_game_context.py tests/test_reflection_prompt.py`

Expected: FAIL (missing semantics text).

---

### Task 2: Implement prompt text updates

**Files:**
- Modify: `prompts/game_context.py`
- Modify: `prompts/reflection_prompt.py`

**Step 1: Update CPD game context**

Add a sentence describing action semantics, e.g.:

```python
"Action semantics: higher action = more cooperation (higher cost), lower action = more self-interest.\n"
```

**Step 2: Update reflection prompt**

Add a brief reminder line (no format change) such as:

```python
"Reminder: higher action = more cooperation; lower action = more self-interest.\n"
```

**Step 3: Run tests to verify they pass**

Run: `CONDA_OVERRIDE_CUDA=0 CONDA_NO_PLUGINS=true conda run -n rgrf python -m unittest tests/test_game_context.py tests/test_reflection_prompt.py`

Expected: PASS.

---

### Task 3: Update logs and run full tests (optional)

**Files:**
- Modify: `ASSISTANT_CHANGELOG.md`
- Modify: `ASSISTANT_ISSUES.md` (only if new issues observed)

**Step 1: Update logs**

Record the CPD semantics clarification and reflection prompt reminder.

**Step 2: Run full test suite**

Run: `CONDA_OVERRIDE_CUDA=0 CONDA_NO_PLUGINS=true conda run -n rgrf python -m unittest discover -s tests`

Expected: PASS.

**Step 3: Commit**

```bash
git add tests/test_game_context.py tests/test_reflection_prompt.py prompts/game_context.py prompts/reflection_prompt.py ASSISTANT_CHANGELOG.md ASSISTANT_ISSUES.md
git commit -m "feat: clarify CPD action semantics in strategic prompts"
```
