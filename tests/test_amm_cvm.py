import unittest

import modules.amm_cvm as amm_cvm


class TestAmmCvmParsing(unittest.TestCase):
    def test_parse_model_params_accepts_final_model_line(self):
        text = "Result: [FINAL_MODEL] alpha: 0.7, beta: 0.3"
        parsed = amm_cvm._parse_model_params(text)
        self.assertEqual(parsed, {"alpha": 0.7, "beta": 0.3})

    def test_parse_model_params_accepts_loose_alpha_beta(self):
        text = "I suggest alpha=0.6, beta=0.4 based on evidence."
        parsed = amm_cvm._parse_model_params(text)
        self.assertEqual(parsed, {"alpha": 0.6, "beta": 0.4})

    def test_parse_model_params_prefers_last_pair(self):
        text = (
            "Earlier: alpha=0.9, beta=0.1. "
            "Final: [FINAL_MODEL] alpha: 0.5, beta: 0.3"
        )
        parsed = amm_cvm._parse_model_params(text)
        self.assertEqual(parsed, {"alpha": 0.5, "beta": 0.3})

    def test_parse_model_params_returns_none_when_missing(self):
        parsed = amm_cvm._parse_model_params("no numbers here")
        self.assertIsNone(parsed)


class TestAmmCvmCorrectionPrompt(unittest.TestCase):
    def test_correction_prompt_emphasizes_output_format(self):
        prompts = []

        def fake_call_llm(prompt, tag=None):
            prompts.append((tag, prompt))
            if tag == "belief":
                return "[FINAL_MODEL] alpha: 0.9, beta: 0.1"
            if tag == "belief_correction":
                return "[FINAL_MODEL] alpha: 1.0, beta: 0.0"
            return ""

        history = [[0.5, 0.5], [0.5, 0.5]]
        last_model = {"alpha": 1.0, "beta": 0.0}
        result = amm_cvm.identify_personality(history, "notes", last_model, fake_call_llm, "CTX")

        correction_prompts = [p for tag, p in prompts if tag == "belief_correction"]
        self.assertTrue(correction_prompts)
        text = correction_prompts[-1].lower()
        self.assertIn("output format", text)
        self.assertIn("final_model", text)
        self.assertIn("exactly", text)
        self.assertEqual(result, {"alpha": 1.0, "beta": 0.0})


if __name__ == "__main__":
    unittest.main()
