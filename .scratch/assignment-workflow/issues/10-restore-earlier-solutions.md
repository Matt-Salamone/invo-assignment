# 10: Restore an earlier solution while preserving assignment history

**What to build:** The student can explicitly restore an earlier worked solution through a traceable operation that keeps later history and unrelated assignment state, then reviews the effect on teaching context.

**Blocked by:** 09: Investigate and correct solution errors with impact review.

**Status:** resolved

- [x] Restoration selects a recorded earlier solution and creates a new traceable history entry identifying the restored revision and reason; it does not erase later Git history.
- [x] Restoration preserves unrelated materials, plans, issued snapshots, returned reports, and evidence records rather than resetting the entire assignment repository.
- [x] Affected lessons, outstanding packets, and evidence receive the same impact review required after a correction. Packet replacement remains explicit, and useful observations are preserved pending relevance assessment.
- [x] A fresh planning conversation can recover the restored solution revision, restoration history, and any pending teaching-context reviews.
- [x] A synthetic black-box full-cycle scenario exercises initialization, intake, verified solution, approved plan, packet issuance, evidence import, confirmed correction with notification and revision history, restoration, and resumption without report loss.
- [x] Focused failure checks demonstrate that an invalid restoration target leaves the current solution and unrelated state intact. All assignment writes remain inside the explicit workspace, leaving source and installed tooling unchanged.



## Answer
Implemented solution-restore selecting only recorded earlier solution revisions. Restores scoped solution artifacts/verification and creates a new traceable Git commit while preserving later history, materials, plan, packets, raw reports and evidence. Uses common correction impact review and durable restoration notifications. Reference: skill/invo-assignment/references/restoration.md. Twenty black-box tests pass; full-cycle test covers intake through report import, correction, invalid target refusal, restoration, retained evidence/report outcomes, Git ancestry and fresh status recovery. New test failed before implementation.
