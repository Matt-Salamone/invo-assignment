# 02: Capture assignment requirements and prepare approved materials

**What to build:** The planning agent turns supplied assignment instructions and course materials into a durable intake record, clarifies consequential uncertainties, and makes approved materials usable without losing their origins.

**Blocked by:** 01: Install the skill and initialize or resume an assignment.

**Status:** resolved

- [x] Intake records required deliverables, constraints, grading criteria, source inventory, consequential uncertainties, and stated assumptions. Routine decisions do not cause unnecessary clarification.
- [x] Deadline and preferred lesson length are optional pacing inputs; unavailable answers do not prevent intake.
- [x] Before a new intake conversion runs, the agent explains its tools, resulting artifacts, and relevant fidelity limits and obtains actual permission. Declined, unavailable, and unreadable materials remain explicit gaps.
- [x] Originals are preserved. Converted derivatives retain provenance and source references sufficient to trace consequential content.
- [x] Supplied course materials govern the assignment context; external sources are distinguished and missing context is exposed rather than invented.
- [x] Skill instructions and public workspace operations persist intake for a new planning conversation. Synthetic behavioral checks cover conversion decisions and provenance, including refusal to record a conversion as approved without the required decision record; instruction dry runs complement checks that cannot prove actual consent.



## Answer
Implemented intake-save and conversion-propose/decide/complete through the public workspace CLI. Requirements, optional pacing, source originals/digests, external references and context gaps persist in state. Conversion completion requires a recorded actual decision following an explained proposal. Reference: skill/invo-assignment/references/intake.md, including consent dry run. Five black-box tests pass (python -m unittest discover -v); conversion test demonstrates missing decision and premature completion refusal plus provenance. Software validates decision records, not human honesty.
