# Restore an earlier worked solution

Use `status` to inspect the current `solution.revision`, `solution_history`, correction reasons and previous verification records. After the student explicitly selects an earlier reference, run:

```text
python <installed-skill>/scripts/workspace.py --workspace <assignment-directory> solution-restore --input <JSON-file>
```

```json
{"revision": "<recorded earlier solution Git revision>", "reason": "Student requested the original worked reference to compare its reasoning"}
```

Only a recorded earlier solution is accepted. The helper reads that solution's artifacts and verification from Git, restores only those files and creates a new commit identifying the earlier revision and reason. Later commits remain ancestors. Unrelated materials, teaching plan, issued packets, raw returned reports and evidence are preserved. Staged changes or uncommitted solution edits must be preserved or committed first. An unknown revision is rejected before writing solution files.

Immediately link the restored artifacts and describe the reason, restored verification results and limitations. Inspect the new `restorations` entry, `notifications` and `impact_reviews`. Follow [teaching-context impact review](corrections.md) for every affected lesson, outstanding packet and earlier evidence. Useful observations remain preserved pending their relevance assessment. Replacement of an outstanding packet remains explicit and never rewrites its snapshot.

Restoration selects earlier content; it does not establish that earlier content is correct. Explain its saved limitations and any confirmed errors being reintroduced so the student can make sense of the comparison. A fresh planning conversation resumes from the new solution revision and pending impact reviews.
