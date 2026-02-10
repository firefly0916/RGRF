# def get_reflection_template(my_action, opp_action, expected_opp, alpha, beta):
#     return f"""
# [Task: Counterfactual Reflection]
# This round, I played: {my_action}
# The opponent played: {opp_action}
# My model (alpha={alpha}, beta={beta}) predicted they would play: {expected_opp}

# [Counterfactual Question]
# If I had played differently (e.g., more cooperative or more defensive), would the opponent have responded better based on their observed sensitivity?
# Is the opponent's personality model (alpha, beta) still accurate?

# [Strategic Note]
# At the end of your response, provide the note in this exact format:
# [FINAL_NOTE] Note: <text>
# """

from prompts.reasoning_prompt import reasoning_instructions


def get_reflection_template(my_action, opp_action, predicted, alpha, beta):
    # 此函数现在主要由 StrategicAgent 内部组装更复杂的 Prompt
    # 这里提供一个基础框架
    return f"""
[Strategic Review: Counterfactual Analysis]
Last Action: {my_action} | Reality: Opponent played {opp_action}
Our Model (alpha={alpha}, beta={beta}) expected them to play {predicted}.

[Task]
Reflect on the gap between reality and prediction. 
Use the provided Counterfactual Experiment (+0.2 action) to determine if we should be more assertive or more cooperative.
Update our strategic approach.

[Output]
{reasoning_instructions()}
[FINAL_NOTE] Note: <text>
"""
