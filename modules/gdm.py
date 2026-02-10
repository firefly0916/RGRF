from library.simulator import predict_future_trajectory
from prompts.decision_prompt import get_decision_template

def decide_action(history, alpha, beta, call_llm):
    # 1. Proposal: LLM 提出 3 个尝试方向
    proposals = [0.2, 0.5, 0.8]
    
    # 2. Evaluation: 使用外部模拟器计算未来收益
    results = []
    for p in proposals:
        expected_score = predict_future_trajectory(p, alpha, beta)
        results.append(f"Proposal Action={p} -> 3-round Expected Score: {expected_score}")
    
    # 3. LLM 决策
    prompt = get_decision_template(history, alpha, beta, "\n".join(results))
    response = call_llm(prompt, tag="decision")
    
    # 解析输出 (假设返回 Action: 0.8)
    return 0.8
