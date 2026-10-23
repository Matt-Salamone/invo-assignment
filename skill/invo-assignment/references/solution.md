# Worked solution and verification

Use course sources as governing context. Save a complete worked solution suited to the actual assignment format, retaining references for consequential claims and reasoning. Read intake gaps and conversion decisions before claiming coverage.

Run `solution-save --input <JSON-file>` with:

- `artifacts`: list of `{source: <prepared-file>, path: <relative-name>}`. Files are copied into `solution/`; existing artifacts are preserved.
- `checks`: list of `{deliverable, result, method, evidence, rubric_coverage}`. Name each required deliverable exactly as in intake; `result` is `passed`, `failed`, or `limited`; `rubric_coverage` lists the grading criteria addressed. Check every deliverable and criterion. Evidence describes actual performed checks, not intended checks.
- `limitations`: list of unresolved correctness issues, missing context and fidelity limits. Failed or limited checks require explicit limitations.

The operation commits solution artifacts and verification to local Git with a tool identity if needed. It returns `solution.revision`, artifact paths, checks and limitations; `status` recovers the same record. Commit or unstage unrelated staged files first. A saved solution with failed checks remains limited; explain those outcomes without claiming full verification.

Immediately provide clickable artifact paths and describe verification and limitations to the student. Access is independent of lesson progress. Explain that this complete worked solution is a learning reference and the later original version is the student's work.

Dry runs for agent judgment:

- Synthetic programming assignment: execute the program against representative and boundary inputs; record actual outputs, required files and rubric coverage. Mark environment-dependent behavior limited if it cannot run.
- Synthetic humanities assignment: check each requested section and length constraint, inspect quotations against supplied passages, and trace claims and citations. Do not replace source inspection with a generic declaration that prose looks correct.
- Synthetic quantitative assignment: recalculate results with an independent method, units and assumptions. Retain the derivation and distinguish a checked calculation from a premise missing in course material.
