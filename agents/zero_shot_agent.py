import re
from agents.base_agent import BaseAgent
from prompts.reasoning_prompt import reasoning_instructions

class ZeroShotAgent(BaseAgent):
    def get_action(self, history, game_rules):
        history = self.clip_history(history)
        prompt = f"""
{game_rules}
Game History (You are index 0): {history}

What is your next action? Think briefly and output your choice.
{reasoning_instructions()}
Format: [FINAL_ACTION] Action: <value between 0 and 1>
"""
        response = self.call_llm(prompt, tag="decision")
        match = re.search(r"\[FINAL_ACTION\]\s*Action:\s*([\d\.]+)", response)
        if match:
            return max(0.0, min(1.0, float(match.group(1))))
        return 0.5
