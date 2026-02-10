import unittest

from agents.strategic_agent import StrategicAgent


class TestStrategicAgent(unittest.TestCase):
    def test_gdm_module_returns_action_without_type_error(self):
        agent = StrategicAgent(name="TestAgent", model_name="dummy-model", api_key="test")
        agent.current_opponent_model = {"alpha": 0.8, "beta": 0.1}
        agent.call_llm = lambda prompt, **kwargs: "[FINAL_ACTION] Action: 0.5"

        action = agent.gdm_module(history=[[0.5, 0.5]], game_rules="Prisoner")

        self.assertEqual(action, 0.5)
