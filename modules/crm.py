from prompts.reflection_prompt import get_reflection_template

def reflect(my_action, opp_action, alpha, beta, call_llm):
    # 预测对比
    expected_opp = round(alpha * my_action - beta, 3)
    
    # LLM 反思
    prompt = get_reflection_template(my_action, opp_action, expected_opp, alpha, beta)
    response = call_llm(prompt, tag="reflection")
    
    # 提取 Note:
    return response.split("Note:")[-1].strip()
