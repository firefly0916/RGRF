import unittest

import prompts.game_context as gc
from prompts.belief_prompt import get_belief_template


class TestGameContext(unittest.TestCase):
    def test_cpd_context_contains_formula(self):
        text = gc.get_game_context("CPD")
        self.assertIn("Prisoner", text)
        self.assertIn("Reward =", text)

    def test_pgg_context_contains_formula(self):
        text = gc.get_game_context("PGG")
        self.assertIn("Public Goods", text)
        self.assertIn("reward", text.lower())

    def test_unknown_context_empty(self):
        self.assertEqual("", gc.get_game_context("OTHER"))

    def test_belief_prompt_includes_context(self):
        text = get_belief_template("hist", "notes", "results", "CTX")
        self.assertIn("Game Context", text)


if __name__ == "__main__":
    unittest.main()
