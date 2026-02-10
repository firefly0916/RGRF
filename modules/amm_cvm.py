# from library.validator import calculate_mse
# from prompts.belief_prompt import get_belief_template

# def identify_personality(history, notes, call_llm):
#     # 1. 模拟 LLM 提出 3 组候选（实际应用中这里可由 LLM 生成）
#     candidates = [(1.0, 0.0), (0.8, 0.1), (0.5, 0.3)] 
    
#     # 2. CVM: 使用外部工具验证
#     results = []
#     for alpha, beta in candidates:
#         mse = calculate_mse(history, alpha, beta)
#         results.append(f"Model(alpha={alpha}, beta={beta}) -> MSE Error: {mse}")
    
#     # 3. LLM 决策
#     prompt = get_belief_template(history, notes, "\n".join(results))
#     response = call_llm(prompt)
    
#     # 解析输出 (简易逻辑)
#     # 假设解析出 alpha, beta
#     return 0.8, 0.1 # 返回示例值


import re
from library.validator import calculate_mse
from prompts.belief_prompt import get_belief_template

def identify_personality(history, notes, last_model, call_llm):
    """
    AMM+CVM 核心模块：
    1. 验证原型性格。
    2. 允许 LLM 结合 Notes 提出修正建议。
    3. 验证建议并做最终锁定。
    """
    # --- 阶段 1: 物理证据收集 ---
    # 定义性格原型作为参照物
    archetypes = [
        {"alpha": 1.0, "beta": 0.0, "label": "Perfect Reciprocity (TFT)"},
        {"alpha": 0.5, "beta": 0.3, "label": "Exploitative/Greedy"},
        {"alpha": 0.0, "beta": 0.0, "label": "Fixed/Unresponsive"},
        {"alpha": last_model["alpha"], "beta": last_model["beta"], "label": "Current Status Quo"}
    ]

    # CVM: 计算这些模型在历史数据上的 MSE 误差 (物理证据)
    results_str = []
    # 去重处理，防止重复计算
    unique_set = {f"{c['alpha']}_{c['beta']}": c for c in archetypes}.values()
    for c in unique_set:
        mse = calculate_mse(history, c["alpha"], c["beta"])
        results_str.append(f"- {c['label']} (alpha={c['alpha']}, beta={c['beta']}) | MSE Error: {mse}")

    # --- 阶段 2: 引导分析与提议 (AMM) ---
    # 使用你定义的 get_belief_template，但增加“提议”指令
    # 告诉 LLM α 和 β 的性格含义，强制它思考“对方为什么变了”
    formatted_results = "\n".join(results_str)
    prompt = get_belief_template(history, notes, formatted_results)
    
    # 第一次调用：让 LLM 进行深度反思并提出最优参数（它可以选原型的，也可以微调）
    response = call_llm(prompt, tag="belief")
    
    # --- 阶段 3: 动态验证 (CVM 2.0) ---
    # 从 LLM 的思考中解析出它想要的 alpha 和 beta
    match = re.search(r"\[FINAL_MODEL\]\s*alpha:\s*([\d\.]+),\s*beta:\s*([\d\.]+)", response)
    
    if match:
        proposed_alpha = float(match.group(1))
        proposed_beta = float(match.group(2))
        
        # 物理验证 LLM 提议的参数是否真的符合历史事实
        proposed_mse = calculate_mse(history, proposed_alpha, proposed_beta)
        
        # --- 阶段 4: 最终锁定 ---
        # 如果 LLM 提议的误差比原型还大，我们要提醒它（防止幻觉）
        if proposed_mse > min([calculate_mse(history, c["alpha"], c["beta"]) for c in archetypes]):
            correction_prompt = f"""
            Wait. Your proposed model (alpha={proposed_alpha}, beta={proposed_beta}) has a high MSE Error of {proposed_mse}.
            This means it doesn't fit the historical data well.
            However, our 'Strategic Notes' say: {notes}
            
            Are you sure you want to deviate from the historically accurate models? 
            If yes, explain why. If no, revert to the most accurate model.
            [FINAL_MODEL] alpha: <val>, beta: <val>
            """
            final_response = call_llm(correction_prompt, tag="belief_correction")
            match = re.search(r"\[FINAL_MODEL\]\s*alpha:\s*([\d\.]+),\s*beta:\s*([\d\.]+)", final_response)
            if match:
                return {"alpha": float(match.group(1)), "beta": float(match.group(2))}

        return {"alpha": proposed_alpha, "beta": proposed_beta}

    # 保底返回
    return last_model
