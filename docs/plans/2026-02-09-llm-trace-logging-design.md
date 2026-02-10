# LLM Trace Markdown Logging Design

**Goal:** 生成易读的 Markdown 追踪日志，按轮次记录每位玩家的 Prompt/Response/Action/Reflection，并保留现有 JSON 结果输出。

**Approach:** 使用 `python-dotenv` 读取 `.env`，在 `run_experiment` 内部构建 `_trace.md` 日志。通过在 `BaseAgent` 中记录 `llm_trace`（包含 tag/model/prompt/response），按轮次截取新增的 trace 条目并写入 Markdown。日志文件命名与 JSON 共享同一时间戳：`results/experiment_<GAME>_<timestamp>_trace.md`。

**Data Flow:**
1. `BaseAgent.call_llm(prompt, tag=None)` 记录 trace 条目（prompt/response/model/tag）。
2. `run_experiment` 在每轮开始记录 trace 游标，轮结束后收集新增 trace，按玩家写入 Markdown。
3. JSON 结果继续保存，但会对 `player_configs` 做脱敏（移除 `api_key`），并追加 `metrics` 字段。

**Logging Format (per round):**
- Round 标题
- 每个玩家块：Action、Payoff
- LLM Calls：按顺序列出 tag/model/Prompt/Response
- Reflection Note（若有）

**Error Handling:**
- 若玩家没有 `llm_trace`，日志中仅记录 Action/Payoff。
- 防止 API key 被写入任何日志。

**Testing:**
- 单元测试验证：单轮运行时 `_trace.md` 文件存在并包含 Prompt/Response/玩家名。
- 单元测试验证：短轮次稳定性指标不会报错；结果文件不会包含 API key。
