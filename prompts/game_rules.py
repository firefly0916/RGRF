CPD_RULES = """
[Game: Continuous Prisoner's Dilemma]
Rules:
1. In each round, you and other players choose a cooperation value 'c' between 0 and 1.
2. Your reward is calculated as: Reward = (1.5 * Average_of_Others_Actions) - Your_Action.
3. If you cooperate more (higher c), you help others but risk losing your own points. 
4. If you cooperate less (lower c), you protect your points but others might stop helping you.
Goal: Maximize your total points over multiple rounds.
"""

PGG_RULES = """
[Game: Public Goods Game]
Rules:
1. You have 1 token per round. You can contribute 'c' (0 to 1) to a common pool.
2. The total pool is multiplied by 2.0 and divided equally among all players.
3. Your reward = (Total_Pool * 2.0 / Total_Players) + (1.0 - Your_Contribution).
4. If everyone contributes, everyone gets rich. If only you contribute, you lose points.
Goal: Maximize your total points over multiple rounds.
"""