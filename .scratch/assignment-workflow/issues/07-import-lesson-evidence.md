# 07: Import lesson evidence without corrupting progress

**What to build:** The student manually returns a lesson chatbot's JSON report, and the planning agent preserves it, validates its association and relevance, and updates progress only from usable observed evidence.

**Blocked by:** 05: Issue and manage one self-contained lesson packet.

**Status:** ready-for-agent

- [ ] Import validates syntax, required structure, assignment, lesson, packet instance, contract version, and solution revision before applying evidence. Returned reports and import outcomes remain available, including rejected attempts.
- [ ] Wrong-assignment associations are rejected; wrong lesson or packet identifiers cannot silently attach evidence to a different lesson. Invalid imports do not advance progress or resolve an outstanding lesson falsely.
- [ ] Duplicate imports do not duplicate progress or suspected-error records. Stale solution revisions trigger relevance review rather than blanket acceptance or automatic loss of observations.
- [ ] Formatting repairs use available information with traceable outcomes. Genuinely missing evidence prompts student input; observations are never invented to satisfy the contract.
- [ ] Progress distinguishes topic coverage, understanding demonstrated with assistance, and understanding demonstrated independently. Agent inferences and recommendations remain distinct from actual observations, and chatbot reports do not establish verified retention or correctness.
- [ ] Valid import records the lesson outcome and preserves suspected errors with reasoning and source locations for later investigation. A fresh planning conversation can recover evidence and outstanding review needs.
- [ ] Synthetic black-box checks cover valid evidence, malformed JSON, missing fields, wrong identifiers, duplicates, stale revision review, and repair requiring missing human evidence.
