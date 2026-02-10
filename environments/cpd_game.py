class CPDGame:
    def __init__(self, k=1.5):
        self.k = k

    def get_payoffs(self, actions):
        """
        多人 CPD 逻辑：收益 = k * (其他人平均贡献) - 自己的贡献
        """
        num_players = len(actions)
        payoffs = []
        for i in range(num_players):
            my_a = actions[i]
            # 计算除我以外其他人的平均值
            others = actions[:i] + actions[i+1:]
            avg_others = sum(others) / len(others) if others else 0
            
            my_score = (self.k * avg_others) - my_a
            payoffs.append(round(my_score, 3))
        return payoffs