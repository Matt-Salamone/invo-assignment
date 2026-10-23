# 09: Investigate and correct solution errors with impact review

**What to build:** Suspected errors from a lesson chatbot, student, or planning agent are investigated against assignment context. Confirmed errors are corrected with revertible history, clear student notification, and review of affected teaching context.

**Blocked by:** 07: Import lesson evidence without corrupting progress.

**Status:** ready-for-agent

- [ ] The same investigation workflow accepts suspicions from any source, including before a lesson report exists. A chatbot assertion alone never authorizes overwriting the worked solution.
- [ ] Investigation records instructions, sources, and reasoning examined, the conclusion, and affected solution parts; unsupported suspicions remain distinguishable from confirmed errors.
- [ ] A confirmed correction is applied without a permission gate, saved in a revertible Git revision with its reason, and announced to the student with an explanation of what changed.
- [ ] Review identifies affected upcoming lessons, outstanding packets, and earlier evidence. An affected outstanding packet requires review before continuation; rebuilding or replacing it is explicit and earlier snapshots remain preserved.
- [ ] Useful older-version observations remain available and receive relevance assessment instead of wholesale removal or unqualified acceptance.
- [ ] Correction reasons, revision history, student-facing notification records, and impact-review outcomes survive a fresh planning conversation.
- [ ] Synthetic public-operation checks cover confirmed and unconfirmed suspicions, pre-report discovery, correction history, an affected pending packet, and retained older evidence. Instruction dry runs assess investigation quality and correction explanation.
