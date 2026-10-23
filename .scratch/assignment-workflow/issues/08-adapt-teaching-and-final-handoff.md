# 08: Adapt teaching and complete the final handoff

**What to build:** The planning agent uses imported lesson evidence to recommend next steps, adapt the teaching plan, and hand control back to the student when teaching ends.

**Blocked by:** 07: Import lesson evidence without corrupting progress.

**Status:** ready-for-agent

- [ ] Valid evidence supports progress explanations and recommendations to revisit material or continue. Routine adaptations such as extra practice, revisiting misconceptions, or reducing redundant teaching apply automatically.
- [ ] Substantial changes in scope or workload are proposed for approval before becoming the active plan. Instructions explain this distinction and durable records preserve the proposal and decision.
- [ ] Students can override progression recommendations. Overrides are recorded as student decisions and do not relabel missing or assisted evidence as independent understanding.
- [ ] When the approved plan is complete, or the student explicitly chooses the final handoff, the agent prompts creation of the student's own original assignment version without prescribing another process.
- [ ] A fresh planning conversation recovers the current plan, adaptations, pending decisions, overrides, and final-handoff status.
- [ ] Synthetic public-operation checks cover routine adaptation, pending substantial changes, approval, overrides, completion, and early final handoff. Structured dry runs assess evidence-based recommendations and manageable pacing.
