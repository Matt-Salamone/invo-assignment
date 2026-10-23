# invo-assignment

A planned agent skill for completing a college assignment as a worked solution, teaching its reasoning through manually transferred lesson packets and reports, and then prompting the student to create their own original version.

**Status: specification ready for implementation.** This repository currently contains the specification, UML design, and development workflow configuration. An installable skill and its helpers have not been implemented yet.

## Specification and design

- [Implementation specification](.scratch/assignment-workflow/spec.md), tracked locally with status `ready-for-agent`.
- [UML design record and previews](docs/design/README.md).

## Intended workflow

1. Install the reusable skill once and initialize a separate local assignment project.
2. Provide instructions and course materials. The planning agent creates and verifies a worked solution, then proposes a teaching plan.
3. Request each lesson, upload its self-contained packet to a fresh chatbot, complete it, and return its JSON report manually.
4. The planning agent adapts the plan and investigates potential mistakes. Confirmed corrections are explained and saved in revertible solution history.
5. Create your own version of the assignment when prompted.

Packets may include summaries or trimmed documents to fit the lesson and chatbot context. Original material and source references are preserved.

## Repository boundaries

This is the public development repository for reusable instructions, scripts, templates, synthetic examples, and tests. A user installs a copy of the skill separately, then keeps each personal assignment in its own local Git repository outside both the source checkout and installed skill directory.

## Development workflow

Specs and tickets use the local Markdown tracker under `.scratch/`; creating this GitHub repository does not change the tracker to GitHub Issues. See [AGENTS.md](AGENTS.md) and the configuration documents it references.

The project is built first for the author's personal use, with future sharing supported by the reusable skill format. Next: derive implementation tickets from the specification.
