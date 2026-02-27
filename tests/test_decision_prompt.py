import unittest

from prompts.decision_prompt import get_decision_template


class TestDecisionPrompt(unittest.TestCase):
    def test_decision_prompt_describes_anchor_role(self):
        text = get_decision_template("H", 1.0, 0.0, "S", "CTX").lower()
        self.assertIn("anchors are reference", text)
        self.assertIn("trend", text)

    def test_decision_prompt_requires_reason_if_deviating(self):
        text = get_decision_template("H", 1.0, 0.0, "S", "CTX").lower()
        self.assertIn("final_action", text)
        self.assertIn("explain", text)
        self.assertIn("diverge", text)


if __name__ == "__main__":
    unittest.main()
