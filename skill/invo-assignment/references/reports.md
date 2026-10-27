# Returned report evidence

The student manually returns the JSON produced by the fresh lesson chatbot. Run `report-import --input <returned-file>`. Original bytes and outcomes are saved under `reports/` and in `imports` even for malformed JSON and rejected associations. A rejection exits nonzero, explains its preserved import ID and leaves progress and the outstanding packet intact. Inspect `status` to recover pending repairs or relevance reviews in a fresh planning chat.

Reports use the exact metadata and structure in the issued `report-template.json` and `report-contract.json`. Require actual observations; coverage, assisted understanding and independent understanding are different evidence levels. The helper preserves observations in `evidence`, records remaining gaps, updates lesson progress to the least independent recorded level, and saves a separate progression recommendation. These reports do not prove correctness, retention or independence beyond the chatbot's observations.

The report's solution revision must match its packet. If that packet's revision is older than the current solution, its context is flagged, or its lifecycle is inactive, import pauses at `needs-review`. Inspect instructions, changed solution and each observation before applying useful evidence. Run `report-review --input <JSON-file>`:

```json
{"import_id": "<saved import UUID>", "relevant_observations": [0], "include_errors": true, "reason": "The question concerns unchanged assignment instructions; its answer remains relevant"}
```

Indices select observations from the preserved report. An empty selection records that no observations currently apply. Older reports remain preserved in either case. Reviewing an old packet does not close a different outstanding packet. Wrong assignment, packet, lesson, contract or packet-solution associations are rejected rather than repaired by guessing. Identical reports, including whitespace-only reformats, do not apply evidence or suspected errors twice. Different reports for an already applied packet also require working from the saved evidence rather than duplicating progress.

For malformed formatting, fix only information supported by the returned file, then run `report-import --input <corrected-file> --repair-of <rejected-import-ID> --repair-note "Removed trailing comma; observations unchanged"`. Preserve the original. If an actual question, learner response or assistance is missing, ask the student to obtain it from the lesson conversation. Never manufacture an answer, label, approval or claimed understanding to make validation pass. A repaired file still receives full validation. Software can require fields and trace repairs; it cannot verify that learner statements are honest.

On valid import, review actual evidence separately from inferred recommendations and student decisions. Suspected errors retain claim, reasoning, source location, originating report and solution revision for investigation; the report alone does not authorize accepting a purported correction as true.

Relevance review rechecks whether another report for that packet was applied while this report awaited review. A conflicting later review is preserved as rejected and cannot duplicate progress or suspected errors.


The same report-import command accepts report_type=side-chat using the embedded supplemental contract. It preserves separate supplemental_reports without adding formal observations or closing a packet. Either report may arrive first. Matching before-answer/unknown help qualifies the effective independence view; original evidence stays intact. Inspect unmatched help and remaining_questions during planning. Read [side-chat roles](side-chat.md).
