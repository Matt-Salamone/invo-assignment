# Workspace operations

Requires Python 3.10+ and Git on PATH. Run `python <installed-skill>/scripts/workspace.py --help` for available operations. Successful commands emit JSON; failures emit a diagnostic on stderr with a nonzero exit status.

Initialize with `python <installed-skill>/scripts/workspace.py --workspace <absolute-assignment-directory> init --name "Assignment name"`. Resume with `status` or repeat `init`; existing state is preserved. Read `.invo/state.json` and the saved assignment artifacts before continuing the next action.

Choose a directory outside the source checkout, installed skill and every other Git repository. Initialization creates a local Git repository; it does not create a remote. Existing unrelated Git repositories require a separate target. Helpers resolve paths and reject escaped output locations, including symlink targets.

All new workflow commands extend this script's operation interface. Use `safe_path(root, relative)` for assignment output paths and `save_state` for durable updates. Preserve the state version and unknown fields when adding workflow records.

For `intake-save` and the three `conversion-*` operations, read [intake payloads and decision flow](intake.md). Each takes `--input <JSON-file>`; the input file may be outside the workspace, while outputs remain confined to it.

For `solution-save --input <JSON-file>`, read [solution artifacts and verification](solution.md).

For `plan-propose` and `plan-approve`, read [teaching plan payload and approval](plan.md).

For `packet-issue`, `packet-resume`, `packet-replace`, `packet-abandon`, read [manual handoff and packet payload](packets.md).

For `report-import` and `report-review`, read [returned evidence, stale review and repair](reports.md).

For `suspicion-record`, `investigation-record`, `correction-apply`, `solution-impact-review`, read [investigations and teaching-context impact](corrections.md).

For `solution-restore`, read [earlier solution selection and history preservation](restoration.md).
