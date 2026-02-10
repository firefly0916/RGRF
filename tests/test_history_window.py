import sys
import types
import unittest

if "openai" not in sys.modules:
    sys.modules["openai"] = types.SimpleNamespace(OpenAI=lambda **kwargs: None)

from agents.base_agent import BaseAgent
from agents.zero_shot_agent import ZeroShotAgent


class DummyBaseAgent(BaseAgent):
    def __init__(self, history_window):
        self.history_window = history_window


class RecordingZeroShot(ZeroShotAgent):
    def __init__(self, history_window=2):
        self.history_window = history_window
        self.last_prompt = None

    def call_llm(self, prompt, tag=None):
        self.last_prompt = prompt
        return "[FINAL_ACTION] Action: 0.5"


class TestHistoryWindow(unittest.TestCase):
    def test_clip_history_keeps_last_n(self):
        agent = DummyBaseAgent(history_window=2)
        history = [[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]]
        clipped = agent.clip_history(history)
        self.assertEqual(clipped, history[-2:])

    def test_zero_shot_prompt_uses_windowed_history(self):
        agent = RecordingZeroShot(history_window=2)
        history = [[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]]
        agent.get_action(history, "RULES")
        self.assertIn(str(history[-2:]), agent.last_prompt)
        self.assertNotIn(str(history), agent.last_prompt)


if __name__ == "__main__":
    unittest.main()
