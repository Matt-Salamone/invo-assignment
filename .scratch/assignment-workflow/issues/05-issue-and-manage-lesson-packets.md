# 05: Issue and manage one self-contained lesson packet

**What to build:** On the student's request, the planning agent stages one preserved, self-contained lesson packet in the mailbox for manual upload to a fresh lesson chatbot. The student can resume, replace, or abandon an outstanding lesson without losing history.

**Blocked by:** 04: Propose and approve the initial teaching plan.

**Status:** ready-for-agent

- [ ] Issuance requires an approved plan and a student request. Each assignment has at most one outstanding packet.
- [ ] A packet includes lesson objectives, tutor instructions, selected worked-solution context and sources, and a structured JSON report contract and template. It identifies assignment, lesson, packet instance, report-contract version, and solution revision.
- [ ] Tutor instructions allow a short opening assessment and require explanations, justifications, targeted follow-up, and reports of actual questions, learner responses, assistance, understanding evidence, remaining gaps, and suspected errors.
- [ ] The issued snapshot and included-material record are preserved; subsequent workspace changes do not silently alter what the student received. The mailbox exposes the current packet clearly.
- [ ] Explicit resume, replacement, and abandonment operations preserve prior snapshots and any returned reports. A fresh planning conversation recovers the outstanding packet and next action.
- [ ] The agent assesses packet size and relevance, records its basis and uncertainty, and discloses limitations when context is unwieldy; automated context reduction is added by ticket 06.
- [ ] Synthetic public-operation checks cover issuance, approval and request prerequisites, single-outstanding enforcement, immutable snapshots, and each lifecycle choice. A dry run verifies a fresh chatbot can use the packet without hidden planning context.
