# Requirements and materials

Save intake using `intake-save --input <JSON-file>` after checking consequential ambiguities with the student. Payload lists: `deliverables`, `constraints`, `grading_criteria`, `uncertainties`, `assumptions`, `sources`. Use optional `deadline` and `preferred_lesson_minutes`; missing pacing answers do not block intake. Each source has unique `id`, `kind` (`course` or `external`), `reference`, `status` (`usable`, `conversion-needed`, `unavailable`, `unreadable`) and optional original file `path`. Available course sources require a file. The helper copies original bytes and records a digest. Initial intake is immutable; explain additional findings in subsequent durable records rather than replacing the original interpretation.

Course sources govern the work. Label external references explicitly. For each uncertainty, record its consequence and either the student's answer or the assumption used. Keep unavailable, unreadable and declined sources visible as context gaps in the solution verification.

Before running an intake conversion:

1. Record `conversion-propose --input <JSON-file>` with `id`, `source_id`, `tool`, `output` (new path under `materials/derived`), `fidelity_limits`, and `source_reference` (pages/slides when applicable). Explain these details to the student.
2. Wait for the actual answer. Record `conversion-decide` with `id`, `decision` (`approved`, `declined`, `unavailable`) and `decision_record` quoting or accurately describing that answer. A proposal or elapsed time is not approval. Software checks the record, not the truth of consent.
3. For approved conversions only, run the explained tool, inspect the derivative for retained content and fidelity loss, and register `conversion-complete` with `id` and `artifact` (the resulting file). The helper preserves a new derivative with original provenance and digest. It does not execute arbitrary converter commands. Report unreadable or missing material explicitly when completion is impossible.

Resume through `status`: intake and conversion decisions remain in the returned durable state.

Instruction dry run: a student supplies scanned slides and declines OCR after hearing its limits. Record the declined decision, leave the original intact, state the missing usable text as a gap and continue using available course content. A fresh planning agent must recover that gap rather than run OCR without a new decision.
