# 09: Investigate and correct solution errors with impact review

**What to build:** Suspected errors from a lesson chatbot, student, or planning agent are investigated against assignment context. Confirmed errors are corrected with revertible history, clear student notification, and review of affected teaching context.

**Blocked by:** 07: Import lesson evidence without corrupting progress.

**Status:** resolved

- [x] The same investigation workflow accepts suspicions from any source, including before a lesson report exists. A chatbot assertion alone never authorizes overwriting the worked solution.
- [x] Investigation records instructions, sources, and reasoning examined, the conclusion, and affected solution parts; unsupported suspicions remain distinguishable from confirmed errors.
- [x] A confirmed correction is applied without a permission gate, saved in a revertible Git revision with its reason, and announced to the student with an explanation of what changed.
- [x] Review identifies affected upcoming lessons, outstanding packets, and earlier evidence. An affected outstanding packet requires review before continuation; rebuilding or replacing it is explicit and earlier snapshots remain preserved.
- [x] Useful older-version observations remain available and receive relevance assessment instead of wholesale removal or unqualified acceptance.
- [x] Correction reasons, revision history, student-facing notification records, and impact-review outcomes survive a fresh planning conversation.
- [x] Synthetic public-operation checks cover confirmed and unconfirmed suspicions, pre-report discovery, correction history, an affected pending packet, and retained older evidence. Instruction dry runs assess investigation quality and correction explanation.



## Answer
Added corrections.py: suspicions from any source, confirmed/unconfirmed investigations against current solution, scoped correction artifacts, full verification coverage, revertible Git commits, durable announcements and conservative impact review for lessons, pending packets and retained evidence. Packet resume is blocked until safe review; replacement stays explicit. Reference: skill/invo-assignment/references/corrections.md with investigation dry run. Fourteen CLI tests pass, including pre-report discovery, unconfirmed refusal, stale revision report review, history and affected pending packet.
