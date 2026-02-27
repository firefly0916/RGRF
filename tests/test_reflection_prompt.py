import unittest

from prompts.reflection_prompt import get_reflection_template


class TestReflectionPrompt(unittest.TestCase):
    def test_reflection_prompt_mentions_action_semantics(self):
        text = get_reflection_template(0.5, 0.5, 0.5, 1.0, 0.0, "CTX")
        self.assertIn("higher action = more cooperation", text.lower())

    def test_reflection_prompt_mentions_avg_others_only(self):
        text = get_reflection_template(0.5, 0.55, 0.5, 1.0, 0.0, "CTX")
        self.assertIn("avg_others", text.lower())
        self.assertIn("do not include your own action", text.lower())

    def test_reflection_prompt_instructs_counterfactual_clamp(self):
        text = get_reflection_template(0.5, 0.5, 0.5, 1.0, 0.0, "CTX").lower()
        self.assertIn("counterfactual_action", text)
        self.assertIn("clamp", text)
        self.assertIn("[0, 1]", text)


if __name__ == "__main__":
    unittest.main()
