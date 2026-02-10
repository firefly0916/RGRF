import os
import unittest
from unittest.mock import patch

from main_experiment import build_default_player_configs, load_api_key


class TestMainExperimentConfig(unittest.TestCase):
    @patch.dict(os.environ, {"OPENROUTER_API_KEY": "k1", "OPENAI_API_KEY": "k2"}, clear=True)
    def test_load_api_key_prefers_openrouter(self):
        self.assertEqual(load_api_key(), "k1")

    @patch.dict(os.environ, {"OPENAI_API_KEY": "k2"}, clear=True)
    def test_load_api_key_fallback_openai(self):
        self.assertEqual(load_api_key(), "k2")

    @patch.dict(os.environ, {}, clear=True)
    def test_load_api_key_missing(self):
        with self.assertRaises(ValueError):
            load_api_key()

    @patch.dict(
        os.environ,
        {
            "OPENROUTER_API_KEY": "k1",
            "OPENROUTER_BASE_URL": "https://openrouter.ai/api/v1",
            "RGRF_MODEL_NAME": "openai/gpt-4o-mini",
        },
        clear=True,
    )
    def test_build_default_player_configs(self):
        configs = build_default_player_configs()
        self.assertEqual(len(configs), 2)
        for cfg in configs:
            self.assertEqual(cfg["config"]["api_key"], "k1")
            self.assertEqual(cfg["config"]["base_url"], "https://openrouter.ai/api/v1")
            self.assertEqual(cfg["config"]["model_name"], "openai/gpt-4o-mini")

    @patch.dict(
        os.environ,
        {
            "RGRF_PLAYER_CONFIGS_JSON": (
                "["
                "{\"style\": \"strategic\", \"config\": {\"model_name\": \"m1\"}},"
                "{\"style\": \"zero_shot\", \"config\": {\"model_name\": \"m2\", \"api_key\": \"k2\"}}"
                "]"
            ),
            "OPENROUTER_API_KEY": "k1",
            "OPENROUTER_BASE_URL": "https://openrouter.ai/api/v1",
        },
        clear=True,
    )
    def test_build_configs_from_json(self):
        configs = build_default_player_configs()
        self.assertEqual(len(configs), 2)
        self.assertEqual(configs[0]["style"], "strategic")
        self.assertEqual(configs[0]["config"]["model_name"], "m1")
        self.assertEqual(configs[0]["config"]["api_key"], "k1")
        self.assertEqual(configs[0]["config"]["base_url"], "https://openrouter.ai/api/v1")
        self.assertEqual(configs[1]["style"], "zero_shot")
        self.assertEqual(configs[1]["config"]["model_name"], "m2")
        self.assertEqual(configs[1]["config"]["api_key"], "k2")
