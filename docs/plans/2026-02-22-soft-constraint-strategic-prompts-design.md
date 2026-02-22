# Soft-Constraint Consistency Checks for Strategic Prompts

## Goal
Introduce lightweight, natural-language “consistency checks” into the strategic agent’s belief/decision/reflection prompts to fix logic breaks (e.g., mismatched semantics, ignored MSE, invalid counterfactuals) without suppressing strategy creativity or changing output formats.

## Scope
- Only strategic agent prompts:
  - `prompts/belief_prompt.py`
  - `prompts/decision_prompt.py`
  - `prompts/reflection_prompt.py`
- No changes to parsing, simulator, or agent flow.
- Output formats remain unchanged: `[FINAL_MODEL]`, `[FINAL_ACTION]`, `[FINAL_NOTE]`.

## Approach
Add a short “logic consistency self-check” block to each prompt. This block is advisory (not rigid), focused on facts and coherence, and designed to preserve emergent strategy choices. The instructions explicitly separate “facts” (observations/metrics) from “inference” (strategy choice), and require a brief rationale when deviating from the most accurate model or from validation signals.

## Consistency Check Content (High-Level)
- **Belief prompt**:
  - If you do not choose the lowest MSE model, explicitly explain why.
  - Use recent history as evidence; do not contradict stated observations.
- **Decision prompt**:
  - Ensure “more cooperative” aligns with higher action in CPD.
  - If chosen action performs worse than a clear anchor, explain the trade-off.
- **Reflection prompt**:
  - Counterfactual actions must be within [0, 1].
  - Pick a meaningful comparison action (not a fixed +0.2 if it exceeds bounds).

## Optional Toggle
Add an environment flag (e.g., `RGRF_CONSISTENCY_CHECK=1`) to enable/disable the check. This allows clean ablations while keeping defaults stable. The helper can live alongside `reasoning_instructions()` or in a new prompt helper file.

## Data Flow
- StrategicAgent constructs prompt → prompt builder injects consistency check → LLM output → existing parser unchanged.
- Validation data (anchors, MSE list) is already present in prompt; the check only points the model to use it consistently.

## Error Handling
- The check must not introduce new required fields.
- If the environment flag is off, prompts should be identical to current behavior.

## Testing Strategy
- Add unit tests that confirm the consistency check text is present when enabled and absent when disabled.
- Ensure no changes to output parsing or tests unrelated to prompt content.

## Success Criteria
- Logs show fewer contradictions (e.g., “more cooperative” with lower action, or ignoring MSE without explanation).
- Strategic agent still produces diverse strategies, but reasoning is more coherent and traceable.
