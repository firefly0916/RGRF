# def get_belief_template(history, notes, candidates_with_errors):
#     return f"""
# [Task: Opponent Modeling]
# Historical Actions (Me, Opponent): {history}
# Strategic Notes from last round: {notes}

# Candidate Personality Models (alpha: reciprocity, beta: greed):
# {candidates_with_errors}

# [Reasoning]
# Based on the prediction errors (MSE) and the Strategic Notes, identify which model best describes the opponent's current state. 
# If the MSE is low, the model is physically accurate. 
# If the Strategic Notes suggest a behavioral shift, consider the model that reflects that shift.

# At the end of your response, provide the final parameters in this exact format:
# [FINAL_MODEL] alpha: <float>, beta: <float>
# """


from prompts.reasoning_prompt import reasoning_instructions


def get_belief_template(history, notes, candidates_with_errors):
    return f"""
[Task: Opponent Personality Recognition]
We model the opponent using: Opponent_Action = (Alpha * Your_Prev_Action) - Beta.
- Alpha (Reciprocity): High means they mirror you; Low means they are indifferent.
- Beta (Greed): High means they deduct a "selfish tax" even if you cooperate.

Current History: {history}
Strategic Memory from CRM: {notes}

Candidate Models & Physical Accuracy (MSE Error - lower is better):
{candidates_with_errors}

[Reasoning]
1. Which model has the lowest MSE? (Historical accuracy)
2. Do the 'Strategic Memory' notes suggest the opponent is changing their behavior?
3. Select or propose the final alpha and beta that best describe them now.

{reasoning_instructions()}
Output Format:
[FINAL_MODEL] alpha: <float>, beta: <float>
"""
