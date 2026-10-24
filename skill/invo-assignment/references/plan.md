# Initial teaching plan

After the worked solution is saved, propose lesson boundaries that explain its reasoning and necessary prerequisites. Start with understanding the assignment instructions. Keep broader course teaching outside the default scope. State lesson objectives, prerequisite knowledge, estimated minutes, total workload and why the chosen boundaries fit the assignment.

Read optional intake `deadline` and `preferred_lesson_minutes`. Compare estimated workload with available time. Explain conflicts and let the student choose reduced scope, shorter sessions or changed timing before approval. Missing pacing preferences do not prevent a proposal.

`plan-propose --input <JSON-file>` example:

```json
{
  "scope": "Understand the synthetic fractions worked example",
  "pacing": "Two ten-minute sessions; no deadline provided",
  "lessons": [
    {"id": "instructions", "kind": "instructions", "title": "Understand the task", "objectives": ["Explain required deliverables"], "prerequisites": [], "minutes": 10},
    {"id": "reasoning", "kind": "solution", "title": "Explain equivalent fractions", "objectives": ["Justify the common denominator"], "prerequisites": ["Meaning of numerator and denominator"], "minutes": 10}
  ]
}
```

Review `teaching/plan.md` with the student. Revise a proposal by repeating `plan-propose`; earlier versions remain in `plan_history`. Record approval only after the student's actual decision using `plan-approve --input <JSON-file>` with `{"version": 2, "decision_record": "Student approved the revised plan"}`. Approving an older version or omitting the decision record fails. The structured `plan` in `status` and human-readable file preserve approval and initial progress for fresh conversations. A proposal authorizes no packet.

Dry run: a synthetic fractions student cannot explain denominators. Add the prerequisite to the solution lesson rather than a general arithmetic course. If the student has fifteen minutes before the deadline and the plan requires twenty, disclose the mismatch and ask which adjustment they choose; record their revised plan approval.
