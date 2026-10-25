# Manual lesson packet handoff

When context is oversized or excessively extraneous, follow [context reduction](reductions.md) before issuance. Include registered derivatives in `context`; their provenance, retention evidence and omissions are preserved in the issued manifest alongside the actual derivative bytes.

Issue one lesson only after the student requests it and the current plan is approved. Read `status` first. `active_packet` identifies the outstanding packet; immutable snapshots remain in `packets` keyed by UUID. The helper replaces `mailbox` with only that packet's flat upload files. Link `mailbox` and tell the student to drag all its files to a fresh chatbot and send Go, then manually return the JSON report. No folder navigation, archive extraction, or extra setup message is required. Keep the complete worked solution independently accessible.

`mailbox` is a disposable upload surface. Bookkeeping lives in `.invo/mailbox.json`, preserved upload views in `uploads/<packet-id>`, and displaced mailbox contents in `.invo/mailbox-history/`. The helper moves old contents outside the mailbox before publishing the new files, preserving pre-existing materials. Completion, abandonment, and early handoff leave the mailbox empty. A legacy `packet-resume` builds an upload view without changing the original packet or its identifiers.

`packet-issue --input <JSON-file>` example:

```json
{
  "lesson_id": "instructions",
  "request_record": "Student asked to begin the instructions lesson",
  "assignment_context": "Create one fractions example and explain its derivation. Show each step; grading considers correctness and reasoning.",
  "context": [{"path": "materials/originals/lecture.txt", "reference": "Lecture 1, section on equivalent fractions"}],
  "upload_profile": {"target_chatbot": "ChatGPT", "max_files": 10},
  "size_assessment": {
    "basis": "One short worked example and one relevant lecture section; inspected file sizes and content",
    "relevance": "Every included passage supports interpreting the task and explaining its requirements",
    "uncertainty": "Use the student's ten-file attachment budget; account upload-rate quota is separate",
    "limitations": []
  }
}
```

Include the assignment instructions, constraints, grading criteria, selected source context and meaningful source references in `assignment_context` and `context`. The helper adds all current solution artifacts automatically and refuses edits that have not been saved as the recorded solution revision. The preserved snapshot includes tutor instructions, report template/contract, manifest with byte counts and digests, selected sources and solution context.

The upload view embeds the tutor instructions, manifest, report template and contract in `lesson.txt`, and concatenates UTF-8 sources into numbered TXT attachments with source boundaries and provenance. Images and PDFs remain separate when they fit. If necessary, PDFs and images are combined into `visual-context.pdf` with source-to-page references; PDF pages keep their content and images retain full pixel dimensions with lossless compression. Transparency is flattened onto white. PDF merging requires optional `pypdf`; image merging also requires `Pillow`. Missing dependencies, unsupported combinations, or remaining budget violations stop issuance before replacing the active packet or mailbox. ZIP files and multiple upload turns are not substitutes for fitting the budget. Inspect combined material for legibility, source mapping, and lesson-critical coverage.

`upload_profile` accepts `target_chatbot`, `max_files`, `max_file_bytes`, and `max_text_bytes`. Successful issuance saves the profile for future packets. The defaults are ChatGPT with a conservative ten-file budget, 20 MiB per attachment, and 2,000,000 UTF-8 bytes per text attachment. These are packaging budgets, not a claim about current service limits. Use a student-supplied budget; otherwise check the target service's current attachment limits and record uncertainty. ChatGPT's per-file token and size limits, rolling upload quotas, project limits, and per-turn attachment limit are distinct. Its [upload help](https://help.openai.com/en/articles/8555545-uploading-files-and-audio-to-chatgpt) describes supported formats, size and rate limits; do not infer a single-turn limit from its rate quota. Recheck when increasing a budget or switching services. A resumed upload view keeps its saved profile; explicitly replace the packet to change packaging.

Inspect every file directly in `mailbox` as if it were the only context available to a new chatbot. Verify its count against `upload_profile.max_files`, file sizes, actual source content, visual fidelity where applicable, identifiers and reporting instructions. Record actual count/bytes in the handoff. Assess relevance before issuance; use [context reduction](reductions.md) for oversized/extraneous material rather than silently omitting lesson-critical content. Preserve exact packet, upload and mailbox bytes in Git (for example with `packets/** -text`, `uploads/** -text`, and `mailbox/** -text` in workspace `.gitattributes`).

Each report identifies `assignment_id`, `lesson_id`, `packet_id`, `contract_version` (1), and `solution_revision`. `observations` contain `criterion`, `question`, `learner_response`, `assistance`, and `evidence_level` (`covered`, `assisted`, `independent`); `remaining_gaps` is a list; `suspected_errors` contain `claim`, `reasoning`, `source_reference`. Reports capture actual interactions, not invented completion assertions. Empty observation lists in the template are placeholders, not evidence. The receiving planner validates returned evidence before progress changes.

Lifecycle commands take JSON through `--input`:

- `packet-resume`: `{"packet_id": "<active UUID>"}` returns the same snapshot. Upload it again if needed.
- `packet-abandon`: add `decision_record` describing the explicit student choice. It closes the outstanding packet and empties the mailbox; history stays intact.
- `packet-replace`: supply the full issuance payload plus `packet_id` identifying the active packet and `decision_record`. It creates a new UUID and snapshot, marking the former packet replaced. Invalid replacement inputs leave the active packet unchanged.

Fresh-chat dry run: drag all files directly from `mailbox` into one fresh-chat turn and send Go. The chatbot should begin teaching immediately and know the task, objective, worked example, source/page references, assessment approach, and exact report identifiers. If it needs the planning chat, additional files, manual regrouping, or a second upload turn, repair the packet before handing it to the student.
