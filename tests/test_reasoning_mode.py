import os
import sys
import types
import unittest

if "openai" not in sys.modules:
    sys.modules["openai"] = types.SimpleNamespace(OpenAI=lambda **kwargs: None)

import prompts.reasoning_prompt as rp
from agents.zero_shot_agent import ZeroShotAgent


class RecordingZeroShot(ZeroShotAgent):
    def __init__(self):
        self.last_prompt = None
        self.history_window = 8

    def call_llm(self, prompt, tag=None):
        self.last_prompt = prompt
        return "[FINAL_ACTION] Action: 0.5"


class TestReasoningPrompt(unittest.TestCase):
    def test_reasoning_instructions_on(self):
        os.environ["RGRF_REASONING_MODE"] = "1"
        try:
            self.assertIn("Reasoning", rp.reasoning_instructions())
            self.assertIn("FINAL", rp.reasoning_instructions())
        finally:
            os.environ.pop("RGRF_REASONING_MODE", None)

    def test_reasoning_instructions_off(self):
        os.environ["RGRF_REASONING_MODE"] = "0"
        try:
            self.assertEqual("", rp.reasoning_instructions())
        finally:
            os.environ.pop("RGRF_REASONING_MODE", None)

    def test_reasoning_prompt_included(self):
        os.environ["RGRF_REASONING_MODE"] = "1"
        try:
            agent = RecordingZeroShot()
            agent.get_action(history=[], game_rules="RULES")
            self.assertIn("[Reasoning]", agent.last_prompt)
        finally:
            os.environ.pop("RGRF_REASONING_MODE", None)


if __name__ == "__main__":
    unittest.main()
