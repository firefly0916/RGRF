# from library.payoff import calculate_cpd_payoff, calculate_pgg_payoff

# def predict_future_trajectory(game_type, my_action, alpha, beta, num_players=2, steps=3):
#     """
#     轨迹模拟器：不仅计算分数，还推演未来多步的互动过程。
#     steps: 模拟的深度（比如推演未来 3 轮）
#     """
    
#     # 我们假设在推演的这段时间内，我的策略导向是固定的（即坚持当前的动作）
#     # 或者可以设计为“我也会根据对手微调”，但为了给 LLM 提供清晰的决策参考，
#     # 我们展示“如果我坚持出这个值，对方会如何演化”。
    
#     trajectory = []
#     current_my_a = my_action
#     total_my_reward = 0
    
#     for i in range(1, steps + 1):
#         # 1. 预测对手基于性格模型产生的响应
#         # 对方动作 t = alpha * 我动作 t-1 - beta
#         pred_others_avg = alpha * current_my_a - beta
#         pred_others_avg = round(max(0.0, min(1.0, pred_others_avg)), 3)
        
#         # 2. 计算该轮收益
#         if game_type == "CPD":
#             my_r, opp_r = calculate_cpd_payoff(current_my_a, pred_others_avg)
#         else: # PGG
#             actions = [current_my_a] + [pred_others_avg] * (num_players - 1)
#             payoffs = calculate_pgg_payoff(actions)
#             my_r = payoffs[0]
        
#         # 记录这一轮的快照
#         trajectory.append({
#             "step": i,
#             "my_action": current_my_a,
#             "opp_avg_action": pred_others_avg,
#             "reward": my_r
#         })
        
#         total_my_reward += my_r
        
#         # 核心：为了实现真正的“多步深度”，在推演中我们假设自己“坚持”初衷动作，下一轮对手的反应将基于这一轮产生的动作
#         # 这里我们假设对手是互惠的，如果我维持高合作，看他是否会慢慢跟上来，观察到对方性格模型对该特定动作的“收敛过程”
#         current_my_a = current_my_a # 这里可以保持固定，看对方的适应曲线
        
#     return {
#         "total_reward": round(total_my_reward, 3),
#         "steps_detail": trajectory
#     }

# library/simulator.py
from library.payoff import calculate_cpd_payoff, calculate_pgg_payoff

def predict_future_trajectory(game_type, my_action, alpha, beta, num_players=2, steps=3):
    """
    轨迹模拟器：返回未来多步的互动过程快照。
    """
    trajectory = []
    current_my_a = my_action
    total_my_reward = 0
    
    # 假设对手基于我上一轮的动作产生反应
    # 为了观察对手的“收敛性”，我们在模拟中保持我的动作固定
    for i in range(1, steps + 1):
        # 对手响应公式: opp = alpha * my_prev - beta
        pred_others_avg = alpha * current_my_a - beta
        pred_others_avg = round(max(0.0, min(1.0, pred_others_avg)), 3)
        
        # 计算收益
        if game_type == "CPD":
            my_r, _ = calculate_cpd_payoff(current_my_a, pred_others_avg)
        else: # PGG
            # PGG 收益 = (总投入 * 2 / 总人数) + (1 - 自己投入)
            total_pool = current_my_a + (pred_others_avg * (num_players - 1))
            my_r = round((total_pool * 2.0 / num_players) + (1.0 - current_my_a), 3)
        
        trajectory.append({
            "step": i,
            "my_action": current_my_a,
            "opp_avg_action": pred_others_avg,
            "reward": my_r
        })
        total_my_reward += my_r
        
    return {
        "total_reward": round(total_my_reward, 3),
        "steps_detail": trajectory
    }