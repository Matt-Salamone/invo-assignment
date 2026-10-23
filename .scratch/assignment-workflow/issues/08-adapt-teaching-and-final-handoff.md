# 08: Adapt teaching and complete the final handoff

**What to build:** The planning agent uses imported lesson evidence to recommend next steps, adapt the teaching plan, and hand control back to the student when teaching ends.

**Blocked by:** 07: Import lesson evidence without corrupting progress.

**Status:** resolved

- [x] Valid evidence supports progress explanations and recommendations to revisit material or continue. Routine adaptations such as extra practice, revisiting misconceptions, or reducing redundant teaching apply automatically.
- [x] Substantial changes in scope or workload are proposed for approval before becoming the active plan. Instructions explain this distinction and durable records preserve the proposal and decision.
- [x] Students can override progression recommendations. Overrides are recorded as student decisions and do not relabel missing or assisted evidence as independent understanding.
- [x] When the approved plan is complete, or the student explicitly chooses the final handoff, the agent prompts creation of the student's own original assignment version without prescribing another process.
- [x] A fresh planning conversation recovers the current plan, adaptations, pending decisions, overrides, and final-handoff status.
- [x] Synthetic public-operation checks cover routine adaptation, pending substantial changes, approval, overrides, completion, and early final handoff. Structured dry runs assess evidence-based recommendations and manageable pacing.


## Answer

Implemented teaching-adapt, teaching-decide, progression-override and final-handoff through the explicit workspace CLI. Routine changes cite imported evidence; substantial proposals preserve the active plan until an actual decision. Overrides remain separate from evidence. Completion checks objectives and gaps; early handoff records student choice and preserves outstanding snapshot history. Fresh sessions recover all decisions and final status. See skill/invo-assignment/references/teaching.md and tests/test_teaching.py.

Validation: adaptation CLI test failed before implementation; synthetic suite exercises routine adaptation, proposal/approval, assisted-evidence override, completion and early handoff.
