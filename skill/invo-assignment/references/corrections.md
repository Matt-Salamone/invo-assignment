# Investigations, corrections and teaching impact

Record a suspicion from a report, student or planning agent before accepting a change. `suspicion-record --input <JSON-file>` takes `source`, `claim`, `reasoning`, `source_reference`. Report-imported suspicions already have IDs. Read `suspected_errors` in status to find the `id`.

Investigate the actual instructions, governing sources and reasoning. `investigation-record` takes:

```json
{"error_id": "<suspicion UUID>", "instructions_examined": ["Task requires an explanation"], "sources_examined": ["Lecture 1, slide 2"], "reasoning": "The example omits the requested justification", "conclusion": "confirmed", "affected_parts": ["solution/answer.txt"]}
```

Use `unconfirmed` when evidence does not establish an error. Both conclusions remain durable. A chatbot assertion by itself is insufficient; explain what you inspected and why the conclusion follows. Reinvestigate against the current solution when a prior investigation is stale.

For a confirmed error, apply the correction without another permission step using `correction-apply`:

```json
{"error_id": "<suspicion UUID>", "artifacts": [{"source": "<prepared corrected file>", "path": "answer.txt"}], "checks": [{"deliverable": "Example", "result": "passed", "method": "Recheck derivation", "evidence": "Every step now justified", "rubric_coverage": []}], "limitations": [], "announcement": "Added the missing explanation required by the task; the numerical result is unchanged."}
```

Verification must cover every intake deliverable and grading criterion, with failed or limited results disclosed. The helper commits the changed solution, preserves the earlier revision and stores correction reason, impact review and student notification. Present the announcement to the student whenever a correction succeeds; a saved notification is a durable record of what must be communicated, not proof the student read it.

Every revision conservatively flags existing teaching context for review. `solution-impact-review` requires `impact_id`, `lessons` keyed by every affected lesson ID, `evidence` keyed by every affected import ID, and `packet` when there was an outstanding packet. Lesson/evidence assessments use `{status: "retained"|"revisit"|"pending", reason: "..."}`. Packet assessment uses `{status: "safe-to-resume"|"replace"|"pending", reason: "..."}`. Assess actual dependencies; retain useful earlier observations and distinguish pending questions from invalidated reasoning. Earlier evidence is preserved, never relabeled as newly observed.

Example impact payload:

```json
{"impact_id": "<impact UUID>", "lessons": {"instructions": {"status": "retained", "reason": "Instructions unchanged"}}, "evidence": {}, "packet": {"status": "replace", "reason": "Old example lacks the required derivation"}}
```

An affected packet cannot resume until explicitly assessed safe. Replacement or abandonment is a separate student decision through packet operations and preserves the old snapshot. Older-version reports still require report relevance review. Never rebuild an issued folder in place.

Dry run: a lesson chatbot claims a sign error. Compare the assignment convention, lecture derivation and calculation independently. If the convention supports the original, record unconfirmed. If a real sign error is established, correct it, rerun calculations, announce affected results, flag lessons using that derivation, and preserve unrelated instruction-reading evidence with a stated relevance reason.
