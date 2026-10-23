# 04: Propose and approve the initial teaching plan

**What to build:** The student can review, revise, and approve a durable teaching plan for understanding the worked solution, with realistic scope and pacing.

**Blocked by:** 03: Create and expose a verified worked solution.

**Status:** resolved

- [x] The proposed plan starts with understanding the assignment instructions, includes necessary prerequisites, and chooses lesson boundaries appropriate to the assignment rather than a fixed subject template.
- [x] Optional deadline and lesson-length preferences inform workload estimates. If proposed work exceeds available time, the agent explains the conflict and lets the student choose an adjustment.
- [x] Initial plan approval is explicitly recorded; a proposal alone does not authorize lesson issuance.
- [x] Human-readable lesson objectives, scope, pacing, approval, and progress coexist with structured state that later operations can use.
- [x] A fresh planning conversation can recover the proposed or approved plan and any pending student decision.
- [x] Public-operation checks cover proposing, revising, approving, and recovering a plan. Synthetic dry runs assess prerequisite coverage and pacing without introducing broader course teaching by default.



## Answer
Implemented plan-propose and plan-approve, preserving revised proposal history and requiring the actual decision record for the current version. Structured plan/progress and teaching/plan.md survive fresh conversations. Skill reference covers assignment instruction first, prerequisites, optional pacing conflict decisions and a synthetic dry run: skill/invo-assignment/references/plan.md. Seven black-box tests pass; new test was red before implementation and validates revision, missing/stale approval refusal and recovery.
