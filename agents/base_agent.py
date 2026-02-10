import datetime
from llm.connector import LLMConnector

class BaseAgent:
    def __init__(self, name, model_name, api_key, base_url=None, history_window=8):
        self.name = name
        self.model_name = model_name
        self.connector = LLMConnector(api_key, base_url)
        self.llm_trace = []
        self.history_window = history_window

    def call_llm(self, prompt, tag=None):
        response = self.connector.send_request(prompt, self.model_name)
        # 增加这一行：将最近一次响应保存在属性中，供实验脚本抓取
        self.last_llm_response = response
        self.last_llm_prompt = prompt
        self.llm_trace.append(
            {
                "tag": tag or "llm_call",
                "model": self.model_name,
                "prompt": prompt,
                "response": response,
                "timestamp": datetime.datetime.now().isoformat(),
            }
        )
        return response

    def clip_history(self, history):
        if history is None:
            return history
        if self.history_window is None:
            return history
        try:
            window = int(self.history_window)
        except (TypeError, ValueError):
            return history
        if window <= 0:
            return []
        if len(history) <= window:
            return history
        return history[-window:]

    def get_action(self, history, game_rules):
        raise NotImplementedError

    def reflect(self, my_action, others_actions):
        """基准模型默认不进行反思，只有 StrategicAgent 会重写此逻辑"""
        pass
