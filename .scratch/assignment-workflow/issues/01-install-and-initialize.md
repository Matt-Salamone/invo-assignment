# 01: Install the skill and initialize or resume an assignment

**What to build:** A student installs the reusable invo-assignment skill separately from its development repository, then initializes an explicit assignment directory or resumes an existing assignment safely. Deliver usable skill instructions and one coherent public workspace-operations interface for deterministic bookkeeping.

**Blocked by:** None (can start immediately).

**Status:** ready-for-agent

- [ ] Installation instructions distinguish the public source repository, installed skill, and personal assignment repository. Installation and updates do not mutate personal assignments.
- [ ] Initialization resolves the actual target location and Git ancestry, rejects targets inside the source checkout, installed skill, or another assignment repository, and never silently adopts an unrelated enclosing repository.
- [ ] A new assignment has a local Git repository without requiring a remote, assignment identity, state-format version, and installed skill version or revision.
- [ ] Repeated initialization resumes existing state without data loss. A fresh planning conversation can identify the assignment and recover its saved status and next action.
- [ ] Helpers require an explicit workspace root and confine assignment writes to it. Later workflow operations extend this same public interface rather than introducing separate tooling seams.
- [ ] Black-box checks use synthetic temporary repositories to demonstrate valid initialization, repeat initialization, unsafe target refusal, and unchanged source and installed tooling.
