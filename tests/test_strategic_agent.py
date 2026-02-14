import unittest

from agents.strategic_agent import StrategicAgent


class TestStrategicAgent(unittest.TestCase):
    def test_gdm_module_returns_action_without_type_error(self):
        agent = StrategicAgent(name="TestAgent", model_name="dummy-model", api_key="test")
        agent.current_opponent_model = {"alpha": 0.8, "beta": 0.1}
        agent.call_llm = lambda prompt, **kwargs: "[FINAL_ACTION] Action: 0.5"

        action = agent.gdm_module(history=[[0.5, 0.5]], game_rules="Prisoner")

        self.assertEqual(action, 0.5)

    def test_gdm_continuous_prompt_allows_free_action_and_logs_validation(self):
        import agents.strategic_agent as strategic_agent

        agent = StrategicAgent(name="TestAgent", model_name="dummy-model", api_key="test")
        agent.current_opponent_model = {"alpha": 0.8, "beta": 0.1}
        agent.llm_trace = []

        def fake_call_llm(prompt, tag=None):
            agent.last_prompt = prompt
            return "[FINAL_ACTION] Action: 0.73"

        def fake_simulator(game_type, my_action, alpha, beta, num_players=2, steps=3):
            return {"total_reward": round(float(my_action), 3), "steps_detail": []}

        original_sim = strategic_agent.predict_future_trajectory
        strategic_agent.predict_future_trajectory = fake_simulator
        agent.call_llm = fake_call_llm

        try:
            action = agent.gdm_module(history=[[0.4, 0.4]], game_rules="Prisoner")
        finally:
            strategic_agent.predict_future_trajectory = original_sim

        self.assertEqual(action, 0.73)
        self.assertIn("Anchor 0.20", agent.last_prompt)
        self.assertIn("Anchor 0.40", agent.last_prompt)
        self.assertIn("Anchor 0.60", agent.last_prompt)
        self.assertIn("NOT limited", agent.last_prompt)
        self.assertTrue(any(e.get("tag") == "decision_validation" for e in agent.llm_trace))
