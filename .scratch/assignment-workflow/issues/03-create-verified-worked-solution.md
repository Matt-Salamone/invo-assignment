# 03: Create and expose a verified worked solution

**What to build:** The planning agent completes the assignment from the intake record and immediately gives the student access to a versioned worked solution, its verification results, and its limitations.

**Blocked by:** 02: Capture assignment requirements and prepare approved materials.

**Status:** resolved

- [x] Skill instructions guide creation of a complete worked solution across assignment types using course materials as governing context and retaining support for consequential reasoning.
- [x] Every required deliverable is checked, with assignment-appropriate correctness checks and rubric coverage recorded. Failed checks and unresolved limitations remain visible.
- [x] Public workspace operations save the initial solution in local Git history and record its revision alongside verification results.
- [x] The student receives accessible solution artifacts and an explanation of verification and limitations immediately, without a lesson-completion gate.
- [x] A fresh planning conversation can recover the solution, its revision, and verification record from durable files.
- [x] Synthetic black-box checks exercise saving and recovering a solution and verification record. Structured instruction dry runs assess sensible verification choices across differing assignment formats without exact prose snapshots.



## Answer
Added solution-save operation with complete deliverable/rubric check coverage, visible failed/limited outcomes, preserved solution artifacts, local Git revision and resumable verification state. Skill links accessible artifacts immediately and includes cross-format verification dry runs: skill/invo-assignment/references/solution.md. Six black-box tests pass; initial red test failed on absent operation, green test recovers artifact from recorded Git revision and status.
