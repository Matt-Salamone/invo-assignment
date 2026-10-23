# 01: Install the skill and initialize or resume an assignment

**What to build:** A student installs the reusable invo-assignment skill separately from its development repository, then initializes an explicit assignment directory or resumes an existing assignment safely. Deliver usable skill instructions and one coherent public workspace-operations interface for deterministic bookkeeping.

**Blocked by:** None (can start immediately).

**Status:** resolved

- [x] Installation instructions distinguish the public source repository, installed skill, and personal assignment repository. Installation and updates do not mutate personal assignments.
- [x] Initialization resolves the actual target location and Git ancestry, rejects targets inside the source checkout, installed skill, or another assignment repository, and never silently adopts an unrelated enclosing repository.
- [x] A new assignment has a local Git repository without requiring a remote, assignment identity, state-format version, and installed skill version or revision.
- [x] Repeated initialization resumes existing state without data loss. A fresh planning conversation can identify the assignment and recover its saved status and next action.
- [x] Helpers require an explicit workspace root and confine assignment writes to it. Later workflow operations extend this same public interface rather than introducing separate tooling seams.
- [x] Black-box checks use synthetic temporary repositories to demonstrate valid initialization, repeat initialization, unsafe target refusal, and unchanged source and installed tooling.



## Answer
Implemented explicit-root init/status CLI in skill/invo-assignment/scripts/workspace.py, with versioned resumable state, local Git initialization and resolved tooling/repository boundary checks. Install instructions: docs/installation.md. Public operation test harness: tests/support.py. Validation: python -m unittest discover -v (3 synthetic black-box cases pass, including symlink escape refusal).
