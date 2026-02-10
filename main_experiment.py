import json
import os
import time
import datetime
from dotenv import load_dotenv
from agents.strategic_agent import StrategicAgent
from agents.zero_shot_agent import ZeroShotAgent
from agents.cot_agent import CoTAgent
from agents.react_agent import ReActAgent
from environments.cpd_game import CPDGame
from environments.pgg_game import PGGGame
from prompts.game_rules import CPD_RULES, PGG_RULES

load_dotenv(override=False)

# 建立一个风格到类的映射表
AGENT_REGISTRY = {
    "strategic": StrategicAgent,
    "zero_shot": ZeroShotAgent,
    "cot": CoTAgent,
    "react": ReActAgent
}


def load_api_key():
    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Missing API key: set OPENROUTER_API_KEY or OPENAI_API_KEY.")
    return api_key


def _default_base_url():
    return (
        os.getenv("OPENROUTER_BASE_URL")
        or os.getenv("OPENAI_BASE_URL")
        or "https://openrouter.ai/api/v1"
    )


def _default_model_name():
    return os.getenv("RGRF_MODEL_NAME") or "openai/gpt-4o"


def _build_player_configs_from_json(raw_json):
    try:
        configs = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        raise ValueError("Invalid RGRF_PLAYER_CONFIGS_JSON: must be valid JSON.") from exc

    if not isinstance(configs, list) or not configs:
        raise ValueError("Invalid RGRF_PLAYER_CONFIGS_JSON: must be a non-empty list.")

    base_url_default = _default_base_url()
    model_name_default = _default_model_name()
    cached_api_key = None

    def get_api_key():
        nonlocal cached_api_key
        if cached_api_key is None:
            cached_api_key = load_api_key()
        return cached_api_key

    normalized = []
    for index, item in enumerate(configs):
        if not isinstance(item, dict):
            raise ValueError(f"Invalid player config at index {index}: expected object.")
        style = item.get("style")
        if not style:
            raise ValueError(f"Missing style in player config at index {index}.")
        config = item.get("config") or {}
        if not isinstance(config, dict):
            raise ValueError(f"Invalid config for player {index}: expected object.")

        new_config = dict(config)
        if "model_name" not in new_config:
            new_config["model_name"] = model_name_default
        if "base_url" not in new_config:
            new_config["base_url"] = base_url_default
        if "api_key" not in new_config:
            new_config["api_key"] = get_api_key()

        normalized.append({"style": style, "config": new_config})
    return normalized


def build_default_player_configs():
    raw_json = os.getenv("RGRF_PLAYER_CONFIGS_JSON")
    if raw_json:
        return _build_player_configs_from_json(raw_json)

    api_key = load_api_key()
    base_url = _default_base_url()
    model_name = _default_model_name()
    return [
        {
            "style": "strategic",
            "config": {
                "model_name": model_name,
                "api_key": api_key,
                "base_url": base_url,
            },
        },
        {
            "style": "zero_shot",
            "config": {
                "model_name": model_name,
                "api_key": api_key,
                "base_url": base_url,
            },
        },
    ]


def rotate_history(history, observer_index):
    """
    通用视角转换：将历史记录中的动作顺序旋转，使观察者 observer_index 的动作始终在 index 0。
    适用于 2 人或多人博弈。
    """
    rotated_history = []
    for round_actions in history:
        # 旋转逻辑：[观察者动作] + [除观察者以外的其他动作]
        new_order = [round_actions[observer_index]] + \
                    round_actions[:observer_index] + \
                    round_actions[observer_index+1:]
        rotated_history.append(new_order)
    return rotated_history


def calculate_advanced_metrics(history, cumulative_scores, game_type):
    num_players = len(cumulative_scores)
    rounds = len(history)
    
    # 1. 合作率 (各玩家平均投入)
    coop_rates = [round(sum(h[i] for h in history) / rounds, 3) for i in range(num_players)]
    
    # 2. 社会福利 (总分)
    social_welfare = round(sum(cumulative_scores), 3)
    
    # 3. 剥削指数 (最高分与最低分的差值)
    exploitation_gap = round(max(cumulative_scores) - min(cumulative_scores), 3)
    
    # 4. 稳定性 (最后2轮动作的平均波动)
    if rounds >= 2:
        stability = round(sum(abs(history[-1][i] - history[-2][i]) for i in range(num_players)) / num_players, 3)
    else:
        stability = 0

    return {
        "cooperation_rates": coop_rates,
        "social_welfare": social_welfare,
        "exploitation_gap": exploitation_gap,
        "stability": stability
    }


def _sanitize_player_configs(player_configs):
    sanitized = []
    for item in player_configs:
        new_item = dict(item)
        config = dict(item.get("config", {}))
        config.pop("api_key", None)
        new_item["config"] = config
        sanitized.append(new_item)
    return sanitized


def _format_trace_entries_md(entries):
    lines = []
    for idx, entry in enumerate(entries, 1):
        tag = entry.get("tag") or "llm_call"
        model = entry.get("model") or "unknown"
        lines.append(f"**Call {idx}** (tag: {tag}, model: {model})")
        lines.append("Prompt:")
        lines.append("```text")
        lines.append(entry.get("prompt", ""))
        lines.append("```")
        lines.append("Response:")
        lines.append("```text")
        lines.append(entry.get("response", ""))
        lines.append("```")
        lines.append("")
    return lines


def run_experiment(game_type, player_configs, rounds=10, save_path="results/"):
    """
    运行完整的博弈实验。
    
    参数说明:
    game_type: "CPD" (连续囚徒困境) 或 "PGG" (公共物品博弈)
    player_configs: 列表，每个元素包含 style 和 config。
    """
    
    # --- 1. 初始化对局环境与玩家 ---
    num_players = len(player_configs)
    game = CPDGame() if game_type == "CPD" else PGGGame()
    rules = CPD_RULES if game_type == "CPD" else PGG_RULES

    agents = []
    for i, p_info in enumerate(player_configs):
        agent_class = AGENT_REGISTRY[p_info["style"]]
        # 实例化智能体
        agent = agent_class(name=f"Player_{i}_{p_info['style']}", **p_info["config"])
        agents.append(agent)

    # 存储原始数据和累积得分
    history = [] 
    cumulative_scores = [0.0] * num_players
    
    # 存储每一轮的详细推理日志 (用于后续分析 LLM 的逻辑)
    detailed_logs = []

    # --- 日志与文件准备 ---
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{save_path}/experiment_{game_type}_{timestamp}.json"
    trace_filename = f"{save_path}/experiment_{game_type}_{timestamp}_trace.md"

    trace_md_lines = [
        f"# Experiment Trace ({game_type})",
        f"- Timestamp: {timestamp}",
        f"- Total Rounds: {rounds}",
        "",
        "## Players",
    ]
    sanitized_players = _sanitize_player_configs(player_configs)
    for i, p_info in enumerate(sanitized_players):
        cfg = p_info.get("config", {})
        trace_md_lines.append(
            f"- Player_{i}_{p_info.get('style')} | model={cfg.get('model_name')} | base_url={cfg.get('base_url')}"
        )
    trace_md_lines.append("")

    # --- 2. 实验循环 ---
    for r in range(rounds):
        print(f"\n" + "="*20 + f" ROUND {r+1} " + "="*20)
        
        current_round_actions = []
        round_thoughts = [] # 存储本轮所有人的思维链
        trace_offsets = {agent.name: len(getattr(agent, "llm_trace", [])) for agent in agents}

        # A. 决策阶段：每个智能体独立出招
        for i, agent in enumerate(agents):
            # 获取当前智能体视角的历史 (自己永远在 index 0)
            personal_history = rotate_history(history, i)
            
            action = 0.5 # 默认动作
            thought = "API_ERROR_NO_THOUGHT"

            # 异常重试逻辑：确保单次 API 失败不毁掉整个长时实验
            for attempt in range(3):
                try:
                    action = agent.get_action(personal_history, rules)
                    # 尝试从 agent 内部获取最后一次推理过程（需在 agent 类中保存 llm 原始响应）
                    thought = getattr(agent, 'last_llm_response', "Thought not captured.")
                    break
                except Exception as e:
                    print(f"Warning: {agent.name} failed at attempt {attempt+1}. Error: {e}")
                    time.sleep(2) # 等待 2 秒后重试
            
            current_round_actions.append(action)
            round_thoughts.append({"player": agent.name, "action": action, "thought": thought})
            print(f"[{agent.name}] Action: {action}")

        # B. 收益计算阶段
        payoffs = game.get_payoffs(current_round_actions)
        for i in range(num_players):
            cumulative_scores[i] += payoffs[i]

        # C. 学习阶段 (CRM 反思)
        round_notes = []
        for i, agent in enumerate(agents):
            my_a = current_round_actions[i]
            others_a = current_round_actions[:i] + current_round_actions[i+1:]
            
            try:
                # 执行反思：对于 StrategicAgent 会产生新的 Note；对于 Baseline 会直接跳过
                agent.reflect(my_a, others_a)
                # 记录反思后的 Strategic Note
                note = getattr(agent, 'strategic_memory', "None")
                round_notes.append({"player": agent.name, "note": note})
            except Exception as e:
                print(f"Reflection failed for {agent.name}: {e}")
                round_notes.append({"player": agent.name, "note": "ERROR"})

        # D. 数据归档
        history.append(current_round_actions)
        
        # 记录本轮所有详细元数据
        detailed_logs.append({
            "round": r + 1,
            "actions": current_round_actions,
            "payoffs": payoffs,
            "reasoning": round_thoughts,
            "strategic_notes": round_notes
        })
        
        print(f"Round Payoffs: {payoffs}")

        # 记录 Markdown 追踪日志（按轮次）
        round_traces = {}
        for agent in agents:
            trace = getattr(agent, "llm_trace", [])
            start_idx = trace_offsets.get(agent.name, 0)
            round_traces[agent.name] = trace[start_idx:]

        trace_md_lines.append(f"## Round {r + 1}")
        for i, agent in enumerate(agents):
            trace_md_lines.append(f"### {agent.name}")
            trace_md_lines.append(f"- Action: {current_round_actions[i]}")
            trace_md_lines.append(f"- Payoff: {payoffs[i]}")
            entries = round_traces.get(agent.name, [])
            if entries:
                trace_md_lines.append("#### LLM Calls")
                trace_md_lines.extend(_format_trace_entries_md(entries))
            note = round_notes[i].get("note") if i < len(round_notes) else None
            if note is not None:
                trace_md_lines.append(f"- Note: {note}")
            trace_md_lines.append("")

    # --- 3. 结果保存 ---
    final_result = {
        "metadata": {
            "game_type": game_type,
            "total_rounds": rounds,
            "player_configs": _sanitize_player_configs(player_configs),
            "timestamp": timestamp
        },
        "final_stats": {
            "total_scores": cumulative_scores,
            "average_scores": [round(s/rounds, 3) for s in cumulative_scores]
        },
        "detailed_data": detailed_logs
    }
    final_result["metrics"] = calculate_advanced_metrics(history, cumulative_scores, game_type)

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(final_result, f, ensure_ascii=False, indent=4)
    with open(trace_filename, 'w', encoding='utf-8') as f:
        f.write("\n".join(trace_md_lines))

    print("\n" + "="*15 + " EXPERIMENT FINISHED " + "="*15)
    print(f"Log saved to: {filename}")
    print(f"Trace saved to: {trace_filename}")
    print(f"Final Cumulative Scores: {cumulative_scores}")

    return history, cumulative_scores

# --- 启动测试 ---
if __name__ == "__main__":
    configs = build_default_player_configs()

    # 运行 CPD 实验，n轮测试
    run_experiment(game_type="CPD", player_configs=configs, rounds=6)
