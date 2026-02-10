import re
from agents.base_agent import BaseAgent

class ReActAgent(BaseAgent):
    def __init__(self, name, model_name, api_key, base_url=None, history_window=8):
        super().__init__(name, model_name, api_key, base_url, history_window=history_window)

    def get_action(self, history, game_rules):
        """
        ReAct 模式：通过 Thought/Action 的结构化提示词引导决策。
        """
        history = self.clip_history(history)
        prompt = f"""
{game_rules}

[Game History]
(The history is from your perspective. Index 0 is YOUR action, others are opponents.)
History: {history}

[Instruction]
Solve this strategic game using the ReAct pattern:
Thought: Analyze the opponent's patterns and your current goal.
Action: Decide on a specific cooperation value between 0 and 1.
Observation: Predict how this action might affect the next state.

You must follow this loop and conclude with your final action in the format: 
[FINAL_ACTION] Action: <value>

Let's begin.
"""
        # 调用基础类的 LLM 接口
        response = self.call_llm(prompt, tag="decision")
        
        # 保存原始响应供实验记录
        self.last_llm_response = response
        
        # 使用正则表达式精准解析动作
        return self._parse_action(response)

    def _parse_action(self, text):
        """
        从 ReAct 的文本流中提取最终动作数值。
        """
        try:
            # 匹配 [FINAL_ACTION] Action: 0.x 格式
            pattern = r"\[FINAL_ACTION\]\s*Action:\s*([\d\.]+)"
            match = re.search(pattern, text)
            if match:
                action = float(match.group(1))
                # 边界约束 [0, 1]
                return max(0.0, min(1.0, action))
            else:
                # 如果没匹配到，尝试搜索最后一个数字（降级方案）
                numbers = re.findall(r"0\.\d+|1\.0|0", text)
                if numbers:
                    return float(numbers[-1])
                return 0.5 # 彻底失败时的保底动作
        except Exception as e:
            print(f"ReAct Parsing Error: {e}")
            return 0.5

    def reflect(self, my_action, others_actions):
        """
        ReActAgent 作为基准模型，默认不进行类似 StrategicAgent 那样的深度反思。
        """
        pass
