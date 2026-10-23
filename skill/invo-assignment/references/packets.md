# Manual lesson packet handoff

Issue one lesson only after the student requests it and the current plan is approved. Read `status` first. `active_packet` identifies the outstanding packet; all snapshots remain in `packets` keyed by immutable UUID. The mailbox file `mailbox/current.json` points to its preserved upload folder. Link that folder and tell the student to manually upload every file in it to a fresh chatbot, then manually return the resulting JSON report. Keep the complete worked solution independently accessible.

`packet-issue --input <JSON-file>` example:

```json
{
  "lesson_id": "instructions",
  "request_record": "Student asked to begin the instructions lesson",
  "assignment_context": "Create one fractions example and explain its derivation. Show each step; grading considers correctness and reasoning.",
  "context": [{"path": "materials/originals/lecture.txt", "reference": "Lecture 1, section on equivalent fractions"}],
  "size_assessment": {
    "basis": "One short worked example and one relevant lecture section; inspected file sizes and content",
    "relevance": "Every included passage supports interpreting the task and explaining its requirements",
    "uncertainty": "The student's chatbot upload limit is unknown",
    "limitations": []
  }
}
```

Include the assignment instructions, constraints, grading criteria, selected source context and meaningful source references in `assignment_context` and `context`. The helper adds all current solution artifacts automatically and refuses edits that have not been saved as the recorded solution revision. The issued folder includes tutor instructions, report template/contract, manifest with byte counts and digests, selected sources and solution context. Inspect the folder as if it were the only context available to a new chatbot. Assess actual size and relevance before issuance; explain upload uncertainty and missing context. Reduce oversized/extraneous context into traceable derivatives before issuance rather than silently omitting lesson-critical content.

Each report identifies `assignment_id`, `lesson_id`, `packet_id`, `contract_version` (1), and `solution_revision`. `observations` contain `criterion`, `question`, `learner_response`, `assistance`, and `evidence_level` (`covered`, `assisted`, `independent`); `remaining_gaps` is a list; `suspected_errors` contain `claim`, `reasoning`, `source_reference`. Reports capture actual interactions, not invented completion assertions. Empty observation lists in the template are placeholders, not evidence. The receiving planner validates returned evidence before progress changes.

Lifecycle commands take JSON through `--input`:

- `packet-resume`: `{"packet_id": "<active UUID>"}` returns the same snapshot. Upload it again if needed.
- `packet-abandon`: add `decision_record` describing the explicit student choice. It closes the outstanding packet and clears the mailbox pointer; history stays intact.
- `packet-replace`: supply the full issuance payload plus `packet_id` identifying the active packet and `decision_record`. It creates a new UUID and snapshot, marking the former packet replaced. Invalid replacement inputs leave the active packet unchanged.

Fresh-chat dry run: hand only the issued folder to the lesson chatbot. It should know the task, objective, worked example, relevant sources, how to assess explanations and how to return observations with the exact identifiers. If it would need the earlier planning chat or an unavailable source file, revise packet context before handing it to the student.
