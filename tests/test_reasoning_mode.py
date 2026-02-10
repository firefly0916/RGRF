import os
import unittest

import prompts.reasoning_prompt as rp


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


if __name__ == "__main__":
    unittest.main()
