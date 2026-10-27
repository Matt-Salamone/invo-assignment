---
name: invo-assignment
description: Complete and verify an assignment, then prepare individually requested lessons using manually transferred packets and returned evidence reports.
---

# Assignment planning

Operate from the student's separate assignment repository. Read [workspace operations](references/operations.md) before initialization or any bookkeeping operation. Use the installed script with an explicit workspace path.

1. Initialize or resume the assignment. Read the returned identity, status and next action. Existing state and durable files govern a fresh planning conversation.
2. Gather instructions and course materials using [intake records and conversion decisions](references/intake.md). Complete the durable requirements and source inventory, including explicit gaps. Ask for optional deadline and lesson duration. Preserve originals. Obtain actual permission after explaining tools, output and fidelity limits before intake conversions.
3. Follow [solution creation and verification](references/solution.md). Save the complete solution with actual checks for every deliverable and rubric criterion in local Git. Immediately link the artifacts and explain verification and limitations.
4. Follow [plan proposal and approval](references/plan.md). Begin with understanding instructions, include necessary prerequisites and reconcile workload with available time. Record approval of the current proposal before issuing lessons.
5. Follow [packet issuance and lifecycle](references/packets.md). Issue a self-contained lesson packet only when requested. Replace `mailbox` with a flat set of upload files within the target chatbot's attachment budget. Link `mailbox`: the student drags all its files to a fresh chatbot and sends Go, then manually returns its evidence report. Preserve snapshots; resume, replace or abandon the single outstanding packet explicitly.
6. Follow [report validation, relevance review and repair](references/reports.md). Preserve questions, answers and assistance; distinguish coverage, assisted understanding and independent understanding. Repair formatting from actual evidence only. Apply routine adaptations; seek approval for substantial scope or workload changes. Record student progression overrides separately from evidence.
7. Follow [investigation, correction and impact review](references/corrections.md). Correct confirmed errors without further permission, preserve revision history, announce the change and assess affected packets and evidence. For an explicit request to restore earlier content, follow [solution restoration](references/restoration.md), preserving later history and unrelated files.
8. When teaching is complete or the student chooses the final handoff, prompt them to create their own original version. The prescribed workflow ends there.

Use [lesson and side-chat roles](references/side-chat.md) for new packets and supplemental reports. Favor useful UML in planning and teaching, accompanied by code/prose and other representations when clearer.

Before ending every user interaction that changed workspace files, follow [workspace Git synchronization](references/workspace-guidance.md#commit-and-push-after-each-interaction): commit the reviewed changes and push the existing verified remote; report failures while preserving local work.

Select assignment-specific reasoning, checks and lesson scope through judgment. Deterministic workspace operations maintain records; they cannot establish the honesty or quality of learner evidence.
