> This project has moved to [invo-learn](https://github.com/Matt-Salamone/invo-learn). This repository and the guidance below are retained as read-only history.

# invo-assignment

This repository develops the reusable invo-assignment skill. Keep personal assignment workspaces in separate repositories outside this repository and the installed skill directory. Use synthetic coursework for examples and tests.

## Agent skills

### Issue tracker

Before creating, reading, or updating specs and tickets, read `docs/agents/issue-tracker.md`. This repository uses local Markdown under `.scratch/`.

### Triage labels

Before assigning or changing issue status, read `docs/agents/triage-labels.md` for the default role vocabulary.

### Domain docs

Before exploring domain behavior or writing a specification, read `docs/agents/domain.md`. This repository uses a single-context glossary and ADR layout.

### UML rendering

Before rendering or revising UML, read `docs/agents/uml-rendering.md`. Probe the local renderer on each invocation. The design record and existing diagram sources are indexed in `docs/design/README.md`.

## Commit and push after each interaction

Before the final response to every user interaction, inspect Git status/diffs,
validate the changes as appropriate, commit the files changed for that interaction,
and push to the verified existing upstream. Skip an empty commit when nothing
changed. Retry an outstanding task push without repeating completed operations.
Stage reviewed task files explicitly; leave unrelated learner/user work intact.
Use an ordinary push, preserve history, and verify the remote branch SHA. If the
remote is absent, unavailable or rejects the push, retain the local commit and
report the exact limitation. Create or change remotes only on explicit request.
Learner records go only to the learner's verified private repository; public
development checkouts contain reusable code, instructions and synthetic examples.
This is an agent end-of-turn responsibility, including planning, preferences,
intake and report work; direct helper calls do not perform it automatically.

## Lesson and side-chat roles

Read `skill/invo-assignment/references/side-chat.md` when changing packet generation, supplemental reports or evidence
projection. Favor useful UML with accompanying code/prose; choose another visual
when clearer. Preserve existing issued packets and original assessment records.
