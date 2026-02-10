# import numpy as np

# def calculate_mse(history, alpha, beta):
#     """
#     计算性格参数与历史的吻合度。
#     history 格式: [[my_a, others_avg_a], ...]
#     """
#     if len(history) < 2: return 0.0
#     errors = []
#     for i in range(1, len(history)):
#         prev_my_action = history[i-1][0]
#         actual_others_avg = history[i][1]
#         # 模型预测: 对方动作 = alpha * 我前一轮动作 - beta
#         predicted_others = alpha * prev_my_action - beta
#         predicted_others = max(0.0, min(1.0, predicted_others))
#         errors.append((actual_others_avg - predicted_others) ** 2)
#     return round(float(np.mean(errors)), 5)


# library/validator.py
import numpy as np

def calculate_mse(history, alpha, beta):
    """
    history 已经是 [[my_a, others_avg], ...] 格式
    """
    if len(history) < 2: return 0.0
    
    errors = []
    for i in range(1, len(history)):
        # 对方本轮动作是由我上一轮动作诱发的
        prev_my_a = history[i-1][0]
        actual_opp_a = history[i][1]
        
        # 预测模型
        pred = max(0.0, min(1.0, alpha * prev_my_a - beta))
        errors.append((actual_opp_a - pred) ** 2)
        
    return round(float(np.mean(errors)), 5)