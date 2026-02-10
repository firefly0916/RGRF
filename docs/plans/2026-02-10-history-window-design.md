# LLM History Window Design

**Goal:** 为所有 LLM agent 引入固定窗口的历史截取，降低 token 成本与延迟，同时不影响全局指标统计。

**Approach:** 在 `BaseAgent` 中增加 `history_window`（默认 8）与 `clip_history(history)`。所有 LLM agent 在拼接 prompt 前统一调用 `clip_history`，只保留最近 N 轮且保持顺序。`StrategicAgent` 先截取再执行“我 + 对手平均”预处理，确保 AMM/CVM 与决策 prompt 使用同一窗口历史。指标统计 `calculate_advanced_metrics` 仍基于全局 history，不受窗口影响。

**Data Flow:**
1. `run_experiment` 传入完整 `history` 给 agent。
2. agent 内部 `clip_history` 生成 `windowed_history`。
3. `windowed_history` 进入 prompt，LLM 输出动作后走原有解析逻辑。

**Config:**
- `history_window` 为可选构造参数；不传则用默认值。
- 配置可在 `player_configs` 中按需覆盖。

**Error Handling:**
- `history` 为空或长度小于窗口时直接返回原值。
- 截取不改变每轮动作结构。

**Testing:**
- 新增单测验证 `clip_history` 行为。
- 新增单测验证 LLM prompt 中只包含最近 N 轮历史。
