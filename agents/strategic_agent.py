import json
import re  # 补充：正则模块
from agents.base_agent import BaseAgent
from library.validator import calculate_mse
from library.simulator import predict_future_trajectory
from prompts.belief_prompt import get_belief_template
from prompts.decision_prompt import get_decision_template
from prompts.reflection_prompt import get_reflection_template

class StrategicAgent(BaseAgent):
    def __init__(self, name, model_name="gpt-4", api_key=None, base_url=None, history_window=8):
        # 补充：支持传入 API Key 和 Base URL 以适配不同 LLM
        super().__init__(name, model_name, api_key, base_url, history_window=history_window)
        self.strategic_memory = "Initial round. No prior notes." 
        self.current_opponent_model = {"alpha": 1.0, "beta": 0.0} 

    def get_action(self, history, game_rules):
        """
        每一轮决策的主入口。
        """
        history = self.clip_history(history)
        # 1. 多人博弈适配逻辑：将历史预处理为 [我, 他人平均] 视角
        # 这一步非常重要，它把复杂的 N 人博弈简化为“我与环境”的二元对立，降低推理负担
        processed_history = []
        for h in history:
            me = h[0]
            # 计算除我以外其他人的平均动作，作为“群体对手”的代表
            others_avg = sum(h[1:]) / len(h[1:]) if len(h) > 1 else h[1]
            processed_history.append([me, others_avg])

        # 2. --- 模块 1 & 2: 动态建模与验证 (AMM+CVM) ---
        # 修改点：确保调用链条打通，传入 self.strategic_memory 和旧模型
        # 这里我们调用内部包装好的 amm_cvm_module
        self.current_opponent_model = self.amm_cvm_module(processed_history)

        # 3. --- 模块 3: 目标导向决策 (GDM) ---
        # 基于更新后的性格模型进行轨迹推演和决策
        # 传入游戏规则以便识别是 CPD 还是 PGG
        final_action = self.gdm_module(processed_history, game_rules)
        
        return final_action

    def amm_cvm_module(self, processed_history):
        """
        内部调度：调用外部动态建模逻辑。
        """
        # 从你专门存放逻辑的文件中导入
        from modules.amm_cvm import identify_personality
        
        # 核心：将“物理证据”、“反思记忆”、“旧模型”全部传进去
        new_model = identify_personality(
            processed_history, 
            self.strategic_memory, 
            self.current_opponent_model, 
            self.call_llm
        )
        
        return new_model

    def gdm_module(self, history, game_rules):
        proposed_actions = [0.2, 0.5, 0.8] 
        simulation_data = []
        alpha = self.current_opponent_model["alpha"]
        beta = self.current_opponent_model["beta"]

        # 补充：识别游戏类型（用于模拟器公式切换）
        game_type = "CPD" if "Prisoner" in game_rules else "PGG"
        num_players = 2 if not history else len(history[0])

        for action in proposed_actions:
            # 补充：向模拟器传递游戏类型和总人数
            expected_long_term_reward = predict_future_trajectory(
                game_type=game_type,
                my_action=action,
                alpha=alpha,
                beta=beta,
                num_players=num_players,
                steps=3,
            )
            simulation_data.append({
                "action": action,
                "expected_reward": expected_long_term_reward
            })

        formatted_simulations = "\n".join([
            f"Proposal Action: {s['action']} | Predicted 3-round Score: {s['expected_reward']}"
            for s in simulation_data
        ])
        
        decision_prompt_text = get_decision_template(history, alpha, beta, formatted_simulations)
        llm_final_choice = self.call_llm(decision_prompt_text, tag="decision")
        
        return self.parse_action(llm_final_choice)

    def reflect(self, my_action, others_actions):
        """
        CRM: 反思模块。支持接收对手动作列表（针对多人）。
        """
        # 补充：多人反思逻辑，计算他人平均值
        avg_others = sum(others_actions) / len(others_actions) if isinstance(others_actions, list) else others_actions

        alpha = self.current_opponent_model["alpha"]
        beta = self.current_opponent_model["beta"]
        predicted_others_move = round(alpha * my_action - beta, 3)

        reflection_prompt_text = get_reflection_template(
            my_action, 
            avg_others, # 传入平均值进行反思
            predicted_others_move, 
            alpha, 
            beta
        )

        reflection_result = self.call_llm(reflection_prompt_text, tag="reflection")
        self.strategic_memory = self.extract_note(reflection_result)
        self.save_memory_to_disk()

    # --- 辅助解析方法 ---
    def parse_params(self, text):
        try:
            # 正则修正：增加对 [FINAL_MODEL] 标签的精准匹配
            pattern = r"\[FINAL_MODEL\]\s*alpha:\s*([\d\.]+),\s*beta:\s*([\d\.]+)"
            match = re.search(pattern, text)
            if match:
                return {"alpha": float(match.group(1)), "beta": float(match.group(2))}
            return {"alpha": 1.0, "beta": 0.0}
        except Exception:
            return {"alpha": 1.0, "beta": 0.0}

    def parse_action(self, text):
        try:
            pattern = r"\[FINAL_ACTION\]\s*Action:\s*([\d\.]+)"
            match = re.search(pattern, text)
            if match:
                return max(0.0, min(1.0, float(match.group(1))))
            return 0.5
        except Exception:
            return 0.5

    def extract_note(self, text):
        try:
            pattern = r"\[FINAL_NOTE\]\s*Note:\s*(.*)"
            match = re.search(pattern, text, re.DOTALL)
            if match:
                return match.group(1).strip()
            return "No strategic insight captured this round."
        except Exception:
            return "Reflection failed."

    def save_memory_to_disk(self):
        # 确保目录存在
        import os
        if not os.path.exists('storage'):
            os.makedirs('storage')
        with open('storage/notes.txt', 'w', encoding='utf-8') as f:
            f.write(self.strategic_memory)


# import json
# from agents.base_agent import BaseAgent
# from library.validator import calculate_mse
# from library.simulator import predict_future_trajectory
# from prompts.belief_prompt import get_belief_template
# from prompts.decision_prompt import get_decision_template
# from prompts.reflection_prompt import get_reflection_template

# class StrategicAgent(BaseAgent):
#     def __init__(self, name, model_name="gpt-4"):
#         super().__init__(name, model_name)
#         self.strategic_memory = "Initial round. No prior notes." # 存储 CRM 生成的备忘录
#         self.current_opponent_model = {"alpha": 1.0, "beta": 0.0} # 存储 AMM+CVM 确定的参数

#     def get_action(self, history, game_rules):
#         """
#         每一轮决策的主入口，执行 AMM+CVM 和 GDM 模块
#         """
#         # --- 模块 1 & 2: 溯因建模 (AMM) 与 因果验证 (CVM) ---
#         # 对应论文：算法 2 (Beliefs over hidden states)
#         self.current_opponent_model = self.amm_cvm_module(history)

#         # --- 模块 3: 目标导向决策 (GDM) ---
#         # 对应论文：算法 3 (Search with proposals) 和 算法 4 (Evaluation)
#         final_action = self.gdm_module(history, game_rules)
        
#         return final_action

#     def amm_cvm_module(self, history):
#         """
#         AMM+CVM: 确定对手的性格参数 (alpha, beta)
#         """
#         # 1. 候选池定义 (可以是 LLM 生成，也可以是预设常用策略)
#         # alpha: 互惠系数, beta: 贪婪系数
#         personality_candidates = [
#             {"alpha": 1.0, "beta": 0.0},  # 完美对等
#             {"alpha": 0.8, "beta": 0.1},  # 略微保守
#             {"alpha": 0.5, "beta": 0.3},  # 贪婪压榨
#             {"alpha": 0.0, "beta": 0.0}   # 随机或固定动作
#         ]

#         # 2. CVM (因果验证): 调用物理工具库计算每个模型的 MSE 误差
#         # 这就是论文中提到的“外部计算工具”调用
#         validation_results = []
#         for candidate in personality_candidates:
#             mse_error = calculate_mse(history, candidate["alpha"], candidate["beta"])
#             validation_results.append({
#                 "params": candidate,
#                 "error": mse_error
#             })

#         # 3. 将验证结果喂给 LLM，让它结合 CRM 的备忘录进行最终“信念”选择
#         formatted_results = "\n".join([
#             f"Model alpha={r['params']['alpha']}, beta={r['params']['beta']} | MSE Error: {r['error']}" 
#             for r in validation_results
#         ])
        
#         belief_prompt_text = get_belief_template(history, self.strategic_memory, formatted_results)
        
#         # LLM 推理输出（期望格式: alpha: 0.8, beta: 0.1）
#         llm_response = self.call_llm(belief_prompt_text)
        
#         # 解析参数（实际开发中需使用正则解析）
#         # 这里模拟解析结果
#         selected_model = self.parse_params(llm_response) 
#         return selected_model

#     def gdm_module(self, history, game_rules):
#         """
#         GDM: 目标导向决策。通过“提案-模拟”找到最优动作。
#         """
#         # 1. 提案 (Proposals): 模拟 LLM 提出不同策略导向的动作
#         # 对应论文算法 3
#         proposed_actions = [0.2, 0.5, 0.8] # 对应防御、中庸、激进合作
        
#         # 2. 世界线模拟 (Simulation): 调用物理模拟器推演未来 3 轮
#         # 对应论文算法 4 (Evaluation)
#         simulation_data = []
#         alpha = self.current_opponent_model["alpha"]
#         beta = self.current_opponent_model["beta"]

#         for action in proposed_actions:
#             # 调用外部工具预测长期收益
#             expected_long_term_reward = predict_future_trajectory(action, alpha, beta, steps=3)
#             simulation_data.append({
#                 "action": action,
#                 "expected_reward": expected_long_term_reward
#             })

#         # 3. LLM 最终决策
#         formatted_simulations = "\n".join([
#             f"Proposal Action: {s['action']} | Predicted 3-round Score: {s['expected_reward']}"
#             for s in simulation_data
#         ])
        
#         decision_prompt_text = get_decision_template(history, alpha, beta, formatted_simulations)
        
#         llm_final_choice = self.call_llm(decision_prompt_text)
        
#         # 解析最终动作
#         final_action = self.parse_action(llm_final_choice)
#         return final_action

#     def reflect(self, my_action, opponent_action):
#         """
#         CRM: 反事实反思模块 (在每一轮游戏结束后运行)
#         """
#         # 获取当前性格模型的预测值，用于对比
#         alpha = self.current_opponent_model["alpha"]
#         beta = self.current_opponent_model["beta"]
#         predicted_opponent_move = round(alpha * my_action - beta, 3)

#         # 构造反思提示词 (CRM)
#         # LLM 将思考：如果我换个做法结果会怎样？我的对手模型准吗？
#         reflection_prompt_text = get_reflection_template(
#             my_action, 
#             opponent_action, 
#             predicted_opponent_move, 
#             alpha, 
#             beta
#         )

#         # LLM 输出将作为下一轮决策的“战略备忘录 (Strategic Note)”
#         reflection_result = self.call_llm(reflection_prompt_text)
        
#         # 更新记忆，存入 storage/notes.txt
#         self.strategic_memory = self.extract_note(reflection_result)
#         self.save_memory_to_disk()

#     # --- 辅助解析方法 ---
#     def parse_params(self, text):
#         """
#         从 LLM 文本中精准提取 alpha 和 beta。
#         期望格式: [FINAL_MODEL] alpha: 0.8, beta: 0.1
#         """
#         try:
#             # 使用正则表达式匹配标识符后的数值
#             pattern = r"\[FINAL_MODEL\]\s*alpha:\s*([\d\.]+),\s*beta:\s*([\d\.]+)"
#             match = re.search(pattern, text)
#             if match:
#                 alpha = float(match.group(1))
#                 beta = float(match.group(2))
#                 return {"alpha": alpha, "beta": beta}
#             else:
#                 print("Warning: Model params not found in LLM output. Using default.")
#                 return {"alpha": 1.0, "beta": 0.0}
#         except Exception as e:
#             print(f"Parsing error: {e}")
#             return {"alpha": 1.0, "beta": 0.0}

#     def parse_action(self, text):
#         """
#         从 LLM 文本中精准提取 Action 数值。
#         期望格式: [FINAL_ACTION] Action: 0.75
#         """
#         try:
#             pattern = r"\[FINAL_ACTION\]\s*Action:\s*([\d\.]+)"
#             match = re.search(pattern, text)
#             if match:
#                 action = float(match.group(1))
#                 # 确保动作在合法区间 [0, 1]
#                 return max(0.0, min(1.0, action))
#             else:
#                 print("Warning: Action not found. Defaulting to 0.5")
#                 return 0.5
#         except Exception as e:
#             print(f"Parsing error: {e}")
#             return 0.5

#     def extract_note(self, text):
#         """
#         提取 CRM 生成的备忘录内容。
#         期望格式: [FINAL_NOTE] Note: 对手很贪婪，建议下轮防御。
#         """
#         try:
#             # 匹配标识符之后的所有文字
#             pattern = r"\[FINAL_NOTE\]\s*Note:\s*(.*)"
#             match = re.search(pattern, text, re.DOTALL) # DOTALL 允许跨行匹配
#             if match:
#                 return match.group(1).strip()
#             else:
#                 return "No strategic insight captured this round."
#         except Exception as e:
#             return f"Error extracting note: {e}"

#     def save_memory_to_disk(self):
#         with open('storage/notes.txt', 'w') as f:
#             f.write(self.strategic_memory)
