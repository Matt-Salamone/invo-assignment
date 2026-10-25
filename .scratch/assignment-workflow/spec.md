# invo-assignment: assignment completion and learning workflow

Status: resolved
Type: spec
Date: 2026-10-23

## Problem Statement

A student needs a repeatable way to turn an assignment and its course materials into a complete worked solution, understand its reasoning thoroughly through lessons, and then create their own original version. Coordinating material preparation, lesson context, fresh chatbot conversations, returned reports, and corrections manually is cumbersome. Progress must survive new planning-agent conversations, and personal coursework must remain separate from the public skill's development repository.

This project is built first for its author's personal use and assessment. It should accommodate different college assignment types through agent judgment rather than constrain the initial release to one subject or assignment family.

## Solution

Provide one independently installable agent skill with templates and small supporting scripts. A user installs it once, opens a separate local assignment project, and asks the planning agent to initialize that workspace.

The workflow has three stages:

1. **Complete the assignment.** Gather instructions and relevant materials, establish the assignment interpretation, clarify consequential ambiguities, prepare approved material conversions, create a complete worked solution, and verify its deliverables and correctness. Make the solution immediately accessible and describe unresolved limitations.
2. **Teach the assignment.** Propose a lesson plan beginning with understanding the assignment instructions. After approval, issue one lesson packet at the student's request. The student manually uploads the packet to a fresh chatbot, completes the lesson, and manually returns its structured report. The planning agent validates the report, updates progress and the plan, and investigates reported solution errors. Repeat until the plan is complete, allowing student overrides of progression recommendations.
3. **Prompt the student to create their own version.** Tell the student to produce their own original assignment. This ends the prescribed workflow; subsequent assistance is the student's choice.

Every assignment has its own local Git repository. A worked solution is version controlled, lesson packets are preserved, reports describe observed evidence, and confirmed corrections are announced to the student without requiring permission to fix them.

## User Stories

1. As a student, I want to install the skill once, so that I can use it across independent assignment projects.
2. As a student, I want installation instructions that distinguish the public source repository, installed skill, and personal assignment repository, so that my coursework has an unambiguous home.
3. As a student, I want to initialize an empty assignment folder through the agent, so that I can begin without assembling the workspace manually.
4. As a student, I want initialization to check the target and its Git root, so that my assignment cannot accidentally become part of the skill repository or another assignment.
5. As a student, I want each assignment to have local Git history without needing a remote, so that changes can be restored locally.
6. As a student, I want to provide all assignment instructions and relevant course materials, so that the agent works from my actual course context.
7. As a student, I want the agent to identify required deliverables, constraints, and grading criteria, so that its interpretation can be checked before it solves the assignment.
8. As a student, I want clarification limited to consequential ambiguities, so that routine assumptions do not interrupt progress unnecessarily.
9. As a student, I want optional deadline and preferred lesson-length inputs, so that the proposed workload reflects my available time.
10. As a student, I want an explanation of proposed material conversions and a permission request before they run, so that I understand their tools, outputs, and fidelity limits.
11. As a student, I want originals preserved and unreadable material identified, so that missing context remains visible.
12. As a student, I want course materials to govern the solution and external sources to be distinguished, so that I can trace consequential reasoning.
13. As a student, I want a complete worked solution tailored to the assignment, so that lessons have a concrete reference.
14. As a student, I want the initial solution checked against all required deliverables and appropriate correctness checks, so that completion has an observable basis.
15. As a student, I want the completed solution immediately accessible with its verification results and limitations, so that I can inspect it whenever I choose.
16. As a student, I want to approve the initial teaching plan, so that its scope and workload match my needs.
17. As a student, I want the first lesson to address understanding the instructions, so that I understand what the assignment asks.
18. As a student, I want necessary prerequisites included, so that gaps do not prevent me from understanding the solution.
19. As a student, I want lesson breakdowns chosen for the assignment, so that the framework works across subjects and deliverable formats.
20. As a student, I want to request lessons individually, so that I control when to begin the next session.
21. As a student, I want one self-contained packet per lesson, so that a fresh chatbot can teach without access to earlier conversations or local files.
22. As a student, I want the agent to assess packet size and extraneous content, so that upload and context limits do not make the lesson impractical.
23. As a student, I want oversized or unfocused context summarized or trimmed into derivative files, so that each packet contains the relevant material.
24. As a student, I want trimmed documents and summaries to retain source references and lesson-critical details, so that reduced context remains usable and traceable.
25. As a student, I want the packet to contain chatbot instructions and a report template, so that the manual handoff is straightforward.
26. As a student, I want optional short opening assessments, so that the chatbot avoids redundant teaching.
27. As a student, I want lessons to ask me to explain reasoning, justify choices, and answer follow-up questions, so that thorough understanding is demonstrated through my responses.
28. As a student, I want reports to record actual questions, answers, and assistance, so that progress is grounded in observed evidence.
29. As a student, I want report identifiers and solution versions checked, so that evidence is associated with the correct assignment and lesson.
30. As a student, I want help repairing malformed reports without invented answers, so that format problems do not corrupt my learning record.
31. As a student, I want each assignment to have only one outstanding packet, so that the current lesson remains clear.
32. As a student, I want explicit choices to resume, replace, or abandon an unfinished lesson, so that I can change direction while preserving history.
33. As a student, I want routine plan adjustments applied automatically, so that reports lead to useful next steps without repeated approvals.
34. As a student, I want substantial changes in scope or workload proposed for approval, so that the agent does not silently expand the plan.
35. As a student, I want to override progression recommendations, so that I retain control of my learning workflow.
36. As a student, I want suspected solution errors recorded in lesson reports, so that the planning agent can investigate them.
37. As a student, I want errors checked against instructions, sources, and reasoning before correction, so that a chatbot assertion alone does not overwrite the solution.
38. As a student, I want confirmed errors fixed without an approval step and explained to me, so that the solution improves with a clear account of changes.
39. As a student, I want solution corrections version controlled and easy to restore, so that a mistaken correction can be undone.
40. As a student, I want corrections reviewed for their effect on packets, lessons, and previous evidence, so that later work uses appropriate context.
41. As a student, I want useful evidence from an older solution version retained and assessed, so that a correction does not unnecessarily erase valid progress.
42. As a student, I want new planning-agent conversations to recover the assignment from its saved state, so that the workflow does not depend on one chat's memory.
43. As a student, I want a simple prompt to create my own version when teaching is complete, so that the final stage remains under my direction.
44. As the maintainer, I want skill development and installation updates separated from assignment mutations, so that updating the tool does not modify personal coursework.
45. As the maintainer, I want the workspace to record the skill version it uses, so that behavior changes can be traced across updates.
46. As the maintainer, I want deterministic bookkeeping handled by small scripts, so that agents can focus on assignment-specific reasoning.
47. As the maintainer, I want synthetic fixtures that exercise the observable workflow, so that the repository can be public without containing personal course materials.
48. As the maintainer, I want to assess usefulness through my own lessons first, so that development follows my experience without requiring a study of other users.

## Implementation Decisions

### Distribution and repository boundaries

- Use one main skill, supported by templates and small scripts where deterministic behavior is useful. Additional skills are justified only if distinct entry points prove necessary.
- Installation and development are separate operations. Ordinary users install the skill rather than fork or clone the development repository to do coursework.
- The public development repository contains reusable instructions, helpers, documentation, templates, and synthetic examples. The installed skill is read as reusable tooling. Each assignment has a separate workspace and local Git repository.
- Initialization takes an explicit target directory, resolves its actual location and Git ancestry, and rejects locations inside the development repository, installed skill directory, or another assignment repository. It must not silently adopt an unrelated enclosing repository.
- Workspace helpers take an explicit workspace root and confine assignment writes to it. They record assignment identity, state-format version, and the installed skill version or revision used.
- A new assignment repository starts locally without a remote. Existing assignment state is resumable rather than silently overwritten by another initialization.

### Responsibilities and durable state

- The planning agent handles assignment interpretation, solution creation, verification, teaching plans, source selection, report interpretation, and correction decisions. It chooses assignment-specific checks and lesson breakdowns.
- The lesson chatbot teaches one issued packet in a fresh conversation and reports observations. It has no implicit access to the planning conversation, other packets, or the assignment filesystem.
- Supporting helpers maintain workspace boundaries, packet snapshots, report validation, state transitions, and Git revision bookkeeping. Expose these through one coherent workspace-operations interface; the command grammar and implementation language are implementation choices.
- Persist instructions, source inventory, originals and derivatives, the worked solution, verification results, lesson plan and progress, issued packets, returned reports, correction history, and relevant identifiers. A later agent must be able to resume from files without the original conversation.
- Human-readable plans and explanations coexist with structured state and report contracts. Durable records distinguish what was observed from what the agent inferred or recommended.

### Intake and the initial solution

- Establish required deliverables, constraints, rubric coverage, and consequential uncertainties before solving. Clarify only ambiguities that materially affect the result; state reasonable assumptions when proceeding.
- Ask for the deadline and preferred lesson length as optional pacing inputs. Estimates are acceptable and can change. Explain when proposed work exceeds available time and let the student choose the adjustment.
- For intake material that requires conversion, explain the tools, resulting artifacts, and relevant fidelity loss, then obtain actual permission before running the conversion. Preserve originals and make declined, unavailable, or unreadable material explicit gaps.
- Use supplied course material as the governing context. Use external sources when needed, distinguish them, and retain references supporting consequential claims or steps. Expose missing context and its effect rather than inventing it.
- Produce the complete worked solution, then verify every required deliverable and apply suitable checks, such as running code, checking calculations, verifying citations, or reviewing rubric coverage. Record what was checked and unresolved limitations.
- Save a versioned initial solution and make it immediately accessible. There is no lesson-completion gate on access to the worked solution.

### Teaching and packet preparation

- Obtain approval of the initial lesson plan. Begin with a lesson on understanding assignment instructions; include the prerequisites needed to explain the solution thoroughly. Broader course teaching is outside the default scope.
- Generate a lesson only when the student requests it. The manual packet/report transfer is an essential workflow requirement rather than an optional integration.
- Build self-contained packets with lesson objectives, tutor instructions, selected solution context and sources, and a structured report contract and template. Include enough context for the fresh chatbot to teach, assess, identify possible mistakes, and produce the report.
- Instruct the lesson chatbot to retrieve and present relevant source content in the chat before a question depends on it. Show readable excerpts or code and accessible visual context with original title and section/page/cell references. The learner should not need to search combined attachments or open provenance paths to answer; preserve exact requirements and leave assessed reasoning to the learner. Opening the learner's project remains appropriate for editing or execution exercises.
- Publish only a flat, ready-to-upload set directly in `mailbox`, replacing its previous contents while preserving displaced material elsewhere. Keep pointers, manifests used only for bookkeeping, immutable packet snapshots and historical uploads outside this surface. The student drags every mailbox file into one fresh chatbot turn and sends Go. Embed tutor/report instructions and source provenance in the uploaded files. Enforce a saved target-chatbot attachment budget (ten files by default), combining text, PDFs or images when needed and preserving lesson-critical content. Reject an over-budget packet before replacing the outstanding packet or mailbox. Completion or abandonment leaves the mailbox empty.
- Assess packet size and relevance for the target chatbot. When selected context is too large or excessively extraneous, summarize it and/or create trimmed derivative files, such as a PDF containing selected lecture slides. This is routine packet preparation authorized by the workflow; it does not require renewed approval for each summary or trimmed copy. The earlier permission requirement still applies to new intake conversions needed to make original materials usable.
- Preserve originals, record included material and derivation provenance with source-page or slide references, and verify that reduction retains lesson-critical details. Identify material limitations rather than silently omitting required context. Exact chatbot limits need not be known to recognize an obviously unwieldy packet; document the basis and any uncertainty.
- A packet identifies its assignment, lesson, packet instance, report-contract version, and worked-solution revision. Preserve the issued snapshot and record what was included so that later workspace changes do not silently change the context the student used.
- Permit only one outstanding packet per assignment. Resume the same packet or explicitly replace or abandon it before issuing another; preserve the earlier snapshot and any reports.

### Lesson evidence and report import

- The chatbot may begin with a brief assessment to gauge prior knowledge and avoid redundant teaching. It then adapts explanation and practice to observed needs.
- Assess understanding through explanations, justification of important choices, and targeted follow-up questions. Choose criteria appropriate to the assignment and record evidence against them.
- A structured JSON report identifies its assignment, lesson, packet instance, contract version, and solution revision. It records actual questions and learner responses, assistance provided, evidence of understanding and remaining gaps, and suspected solution errors with relevant reasoning or source locations.
- Distinguish covering a topic, demonstrating understanding with assistance, and demonstrating understanding independently. A report is evidence from a chatbot session, not software-verified proof of independence, correctness, or long-term retention.
- Validate syntax, required structure, identifiers, and revision relevance before applying a report. Preserve returned reports and import outcomes. Help repair formatting from available information and ask for genuinely missing evidence; never fabricate observations to satisfy the contract.
- Reject wrong-assignment associations. Treat duplicated imports without duplicating progress or corrections. Review stale-version reports for relevance instead of either accepting all conclusions or discarding all observations automatically.
- Update progress from valid evidence. Recommend revisiting material or continuing, while allowing the student to override progression. Preserve an override as a student decision rather than relabeling it as demonstrated understanding.

### Plan adaptation, solution corrections, and restoration

- Apply routine adaptations automatically, including extra practice, revisiting a misconception, and reducing teaching of already-understood material. Request approval for substantial changes in scope or workload.
- Investigate a suspected solution error against instructions, sources, and reasoning before correcting it, regardless of whether it was reported by the chatbot, student, or planning agent.
- Correct a confirmed error without asking for permission. Preserve a revertible Git revision and record the reason and affected solution parts. Inform the student whenever a correction is made.
- Assess effects on upcoming lessons, outstanding packets, and earlier evidence. Flag an affected outstanding packet for review before continuation. Preserve earlier snapshots; rebuilding or replacing the active packet is explicit.
- Restore an earlier solution through an explicit, traceable operation that preserves later history. Review dependent lesson context and evidence after restoration, just as after a correction; restoration must not erase unrelated materials, plans, or reports.
- When the approved plan is complete, or the student explicitly chooses the final handoff, tell the student to create their own original version. Specify no further phase-three process.

## Testing Decisions

- **Confirmed testing boundary:** exercise the public workspace helper operations as a black box in temporary assignment repositories. Drive initialization, packet issuance, report import, progress updates, solution correction, and restoration through that boundary. Inspect externally visible files, status, and Git history rather than private functions or data structures.
- Test the coherent workspace-operations interface and its observable contracts, including installation/source separation, source provenance, packet lifecycle, report validation, correction history, and resumability. Separate public operations may be used within that one test boundary; do not introduce test-only production interfaces.
- Good tests demonstrate meaningful behavior or failure handling. They should survive internal refactors and avoid exact prose snapshots, tests mirroring implementation, or unnecessary assertions about internal layout.
- Cover initialization in a separate target, repeated initialization without data loss, and refusal of targets within tooling or unrelated repositories. Confirm assignment operations leave the development repository and installed skill unchanged.
- Use a small synthetic assignment for a full cycle: initialize, save and verify a worked solution, approve a plan, issue a packet, import an evidence-bearing report, correct a confirmed error with notification and revision history, and restore an earlier solution without losing reports.
- Exercise invalid and missing report fields, wrong identifiers, duplicate imports, stale solution revisions, and repair requiring missing human evidence. Invalid imports must not falsely advance progress.
- Exercise an outstanding packet followed by resume, replacement, or abandonment; correction of source context affecting a pending lesson; and resumption by a new planning session from durable files.
- Exercise packet reduction with synthetic source pages: retained content supports the lesson, original files remain unchanged, source references match the derivative, and omitted relevant context is reported. Validate selected-page PDFs through actual page content or rendering where practical rather than their filenames alone.
- Verify that the solution restoration operation preserves history and unrelated state and prompts review of affected teaching context.
- Behavioral checks on permission and approval requirements should exercise records and state transitions where helpers support them. A schema or script cannot itself prove that an agent taught well or obtained an honest learner response.
- Use structured dry runs and the author's own real lessons for instruction quality, sensible material selection, assignment-specific verification, assessment usefulness, and manageable pacing. These complement deterministic helper tests; there is no required efficacy study involving other students.
- **Prior art:** the new repository currently contains setup documentation only, so there is no existing test suite or established code seam to reuse. The related invo-learn project provides conceptual precedent for packet and report contracts; this specification does not require that runtime or imply that its tests validate this new implementation.
- The author confirmed this boundary in the design conversation on 2026-10-23. This document specifies future implementation tests; no skill implementation is included in this change.

## Out of Scope

- A prescribed process, assessment system, or coaching protocol for the student's own-version stage beyond its opening prompt.
- Automatic chatbot uploads, report retrieval, background lesson scheduling, calendar integration, or a direct-teaching replacement for the mandatory manual handoff.
- A dependency on the invo-learn application, or a broad migration of its runtime and existing course data.
- Restricting support to a particular college course, discipline, or assignment format.
- A full course curriculum beyond prerequisites needed for the assignment.
- A mandatory learning-efficacy study, recruitment of other students, or verified retention claims.
- Automatic publication or remote hosting of personal assignment repositories.
- A marketplace/plugin release, multiple skill entry points, or a large application framework for the initial implementation.

## Further Notes

### Working vocabulary

- **Worked solution:** the planning agent's completed and verified assignment artifact, retained as a versioned teaching reference.
- **Planning agent:** the agent operating in the assignment project and maintaining its durable state.
- **Lesson chatbot:** a fresh chatbot conversation supplied only with the issued lesson packet and the student's contributions.
- **Packet:** a preserved, self-contained set of files prepared for one lesson and manually transferred by the student.
- **Mailbox:** the visible staging location for the current packet, backed by preserved issued-packet history.
- **Report:** the structured account of lesson observations manually returned to the planning agent.
- **Assignment workspace:** the personal local repository holding one assignment's materials, worked solution, learning state, and history.

### Design references and scope

The workflow diagrams describe proposed design rather than existing software. The sequence is split into intake/solution/plan and lesson-cycle/final-handoff panels. The installation diagram shows the public source, installed skill, and assignment repository boundaries.

- [Design record and diagram identities](../../docs/design/README.md)
- [Workflow PlantUML source](../../docs/design/assignment-workflow.puml)
- [Intake, solution, and plan preview](../../docs/design/assignment-workflow.svg)
- [Lesson cycle and final handoff preview](../../docs/design/assignment-workflow_001.svg)
- [Installation boundaries source](../../docs/design/installation-boundaries.puml)
- [Installation boundaries preview](../../docs/design/installation-boundaries.svg)

The author agreed to the workflow through proposed design v2 and the installation/workspace boundary design. This specification consolidates those decisions and the confirmed testing boundary. Command names, implementation language, exact internal layout, and field spelling remain implementation choices under the contracts above. There are no known unresolved product decisions blocking this specification.

The related [invo-learn project](https://github.com/Matt-Salamone/invo-learn) is a reference for manual packets and reports, not a required dependency. The [official skill guidance](https://learn.chatgpt.com/docs/build-skills) describes reusable skill directories and installation; the initial release targets standalone installation.

## Implementation outcome

Implemented on integration branch codex/assignment-workflow. All ten tickets are resolved. Twenty-three synthetic public-operation tests pass, including full-cycle restoration and regressions for correction-impact eligibility, duplicate relevance-review imports, and shared plan validation. Standards and spec reviews completed; all actionable findings were fixed. Instruction dry-run scenarios are documented in docs/testing-dry-runs.md; live lesson usability remains for personal assessment.
