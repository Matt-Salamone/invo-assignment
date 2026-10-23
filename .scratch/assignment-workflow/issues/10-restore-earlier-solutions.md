# 10: Restore an earlier solution while preserving assignment history

**What to build:** The student can explicitly restore an earlier worked solution through a traceable operation that keeps later history and unrelated assignment state, then reviews the effect on teaching context.

**Blocked by:** 09: Investigate and correct solution errors with impact review.

**Status:** ready-for-agent

- [ ] Restoration selects a recorded earlier solution and creates a new traceable history entry identifying the restored revision and reason; it does not erase later Git history.
- [ ] Restoration preserves unrelated materials, plans, issued snapshots, returned reports, and evidence records rather than resetting the entire assignment repository.
- [ ] Affected lessons, outstanding packets, and evidence receive the same impact review required after a correction. Packet replacement remains explicit, and useful observations are preserved pending relevance assessment.
- [ ] A fresh planning conversation can recover the restored solution revision, restoration history, and any pending teaching-context reviews.
- [ ] A synthetic black-box full-cycle scenario exercises initialization, intake, verified solution, approved plan, packet issuance, evidence import, confirmed correction with notification and revision history, restoration, and resumption without report loss.
- [ ] Focused failure checks demonstrate that an invalid restoration target leaves the current solution and unrelated state intact. All assignment writes remain inside the explicit workspace, leaving source and installed tooling unchanged.
