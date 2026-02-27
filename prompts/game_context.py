
def get_game_context(game_type):
    if game_type == "CPD":
        return (
            "Game: Continuous Prisoner's Dilemma\n"
            "Reward = (1.5 * Average_of_Others_Actions) - Your_Action\n"
            "Action semantics: higher action = more cooperation (higher cost), lower action = more self-interest.\n"
            "Action range: 0 to 1\n"
        )
    if game_type == "PGG":
        return (
            "Game: Public Goods Game\n"
            "Reward = (Total_Pool * 2.0 / Total_Players) + (1.0 - Your_Contribution)\n"
            "Action range: 0 to 1\n"
        )
    return ""
