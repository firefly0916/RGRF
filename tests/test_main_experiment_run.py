import json
import os
import tempfile
import unittest

import main_experiment as me


class DummyAgent:
    def __init__(self, name, **config):
        self.name = name
        self.last_llm_response = "dummy"
        self.llm_trace = []

    def get_action(self, history, game_rules):
        self.last_llm_response = "dummy"
        self.llm_trace.append(
            {
                "tag": "decision",
                "model": "dummy-model",
                "prompt": "prompt?",
                "response": "response!",
            }
        )
        return 0.5

    def reflect(self, my_action, others_actions):
        self.llm_trace.append(
            {
                "tag": "reflection",
                "model": "dummy-model",
                "prompt": "reflect?",
                "response": "note",
            }
        )
        return None


class TestMainExperimentRun(unittest.TestCase):
    def test_calculate_advanced_metrics_single_round(self):
        history = [[0.5, 0.6]]
        cumulative_scores = [1.0, 2.0]
        metrics = me.calculate_advanced_metrics(history, cumulative_scores, "CPD")
        self.assertEqual(metrics["stability"], 0)

    def test_run_experiment_redacts_api_key_and_returns_two_values(self):
        original_registry = me.AGENT_REGISTRY
        me.AGENT_REGISTRY = {"dummy": DummyAgent}
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                player_configs = [
                    {
                        "style": "dummy",
                        "config": {
                            "model_name": "m",
                            "api_key": "secret",
                            "base_url": "http://example.com",
                        },
                    }
                ]
                result = me.run_experiment(
                    game_type="CPD",
                    player_configs=player_configs,
                    rounds=1,
                    save_path=tmpdir,
                )
                self.assertIsInstance(result, tuple)
                self.assertEqual(len(result), 2)

                files = [f for f in os.listdir(tmpdir) if f.endswith(".json")]
                self.assertEqual(len(files), 1)
                with open(os.path.join(tmpdir, files[0]), "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                saved_config = data["metadata"]["player_configs"][0]["config"]
                self.assertNotIn("api_key", saved_config)
        finally:
            me.AGENT_REGISTRY = original_registry

    def test_run_experiment_writes_trace_md(self):
        original_registry = me.AGENT_REGISTRY
        me.AGENT_REGISTRY = {"dummy": DummyAgent}
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                player_configs = [{"style": "dummy", "config": {"model_name": "m", "api_key": "k"}}]
                me.run_experiment(
                    game_type="CPD",
                    player_configs=player_configs,
                    rounds=1,
                    save_path=tmpdir,
                )
                md_files = [f for f in os.listdir(tmpdir) if f.endswith("_trace.md")]
                self.assertEqual(len(md_files), 1)
                with open(os.path.join(tmpdir, md_files[0]), "r", encoding="utf-8") as fh:
                    content = fh.read()
                self.assertIn("Round 1", content)
                self.assertIn("Player_0_dummy", content)
                self.assertIn("Prompt", content)
                self.assertIn("Response", content)
        finally:
            me.AGENT_REGISTRY = original_registry
