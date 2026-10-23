# 07: Import lesson evidence without corrupting progress

**What to build:** The student manually returns a lesson chatbot's JSON report, and the planning agent preserves it, validates its association and relevance, and updates progress only from usable observed evidence.

**Blocked by:** 05: Issue and manage one self-contained lesson packet.

**Status:** resolved

- [x] Import validates syntax, required structure, assignment, lesson, packet instance, contract version, and solution revision before applying evidence. Returned reports and import outcomes remain available, including rejected attempts.
- [x] Wrong-assignment associations are rejected; wrong lesson or packet identifiers cannot silently attach evidence to a different lesson. Invalid imports do not advance progress or resolve an outstanding lesson falsely.
- [x] Duplicate imports do not duplicate progress or suspected-error records. Stale solution revisions trigger relevance review rather than blanket acceptance or automatic loss of observations.
- [x] Formatting repairs use available information with traceable outcomes. Genuinely missing evidence prompts student input; observations are never invented to satisfy the contract.
- [x] Progress distinguishes topic coverage, understanding demonstrated with assistance, and understanding demonstrated independently. Agent inferences and recommendations remain distinct from actual observations, and chatbot reports do not establish verified retention or correctness.
- [x] Valid import records the lesson outcome and preserves suspected errors with reasoning and source locations for later investigation. A fresh planning conversation can recover evidence and outstanding review needs.
- [x] Synthetic black-box checks cover valid evidence, malformed JSON, missing fields, wrong identifiers, duplicates, stale revision review, and repair requiring missing human evidence.



## Answer
Implemented reports.py through report-import/report-review, preserving raw bytes and rejected outcomes, validating all packet identifiers and observed evidence, canonical duplicate detection, inactive/stale relevance review, traceable evidence-backed format repair and distinct progression recommendations. Reference: skill/invo-assignment/references/reports.md. Twelve black-box tests pass, including malformed JSON, missing response, wrong IDs, duplicate, relevance review and repair. Initial tests failed before operation existed. Stale solution revision review is implemented; actual correction-cycle coverage is added with ticket 09.
