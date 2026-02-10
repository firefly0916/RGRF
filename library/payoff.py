def calculate_cpd_payoff(my_action, opp_action, k=1.5):
    my_score = (k * opp_action) - my_action
    opp_score = (k * my_action) - opp_action
    return round(my_score, 3), round(opp_score, 3)

def calculate_pgg_payoff(actions, multiplier=2.0):
    num_players = len(actions)
    total_pool = sum(actions)
    share = (total_pool * multiplier) / num_players
    # 返回列表：[p0收益, p1收益...]
    return [round(share + (1.0 - a), 3) for a in actions]