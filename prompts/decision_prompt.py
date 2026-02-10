# def get_decision_template(history, alpha, beta, proposals_with_scores):
#     return f"""
# [Task: Goal-Directed Decision]
# Opponent Character: Alpha={alpha} (Reciprocity), Beta={beta} (Greed).
# Current History: {history}

# Evaluated Proposals (Calculated by Simulator):
# {proposals_with_scores}

# [Reasoning]
# Analyze the long-term expected rewards of each proposal. 
# A higher cooperation (my_action) might lead to higher long-term trust, while low cooperation prevents exploitation.
# Choose the proposal that maximizes long-term utility according to our goal.

# At the end of your response, provide the chosen action in this exact format:
# [FINAL_ACTION] Action: <float>
# """

from prompts.reasoning_prompt import reasoning_instructions


def get_decision_template(history, alpha, beta, simulation_summary):
    return f"""
[Goal-Directed Decision: Trajectory Search]
Current Opponent Model: Alpha={alpha}, Beta={beta}.
(They respond to you with: {alpha} * your_action - {beta})

Future Simulations (3-round depth):
{simulation_summary}

[Strategic Task]
Compare the proposals. 
- Look for "Pathways to Cooperation": An action might be low-reward now, but leads to high mutual gain by Step 3.
- Observe the "Risk Case": If the worst-case reward is too low, the action is dangerous.
Choose the action that best balances stability and profit.

{reasoning_instructions()}
Format: [FINAL_ACTION] Action: <val>
"""
