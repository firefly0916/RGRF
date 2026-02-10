class PGGGame:
    def __init__(self, multiplier=2.0):
        self.multiplier = multiplier

    def get_payoffs(self, actions):
        """
        公共物品博弈：收益 = (总池子 * 倍数 / 总人数) + (1 - 自己的贡献)
        """
        num_players = len(actions)
        total_pool = sum(actions)
        share = (total_pool * self.multiplier) / num_players
        
        payoffs = [round(share + (1.0 - a), 3) for a in actions]
        return payoffs