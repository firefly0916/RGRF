import unittest

from prompts.belief_prompt import get_belief_template


class TestBeliefPrompt(unittest.TestCase):
    def test_belief_prompt_emphasizes_output_format(self):
        text = get_belief_template([], "notes", "- MSE", "CTX").lower()
        self.assertIn("output format", text)
        self.assertIn("final_model", text)
        self.assertIn("exactly", text)


if __name__ == "__main__":
    unittest.main()
