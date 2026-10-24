# Reduce lesson context

Before issuing oversized or excessively extraneous context, inspect actual content and sizes. Record why selected material supports the objectives, target chatbot when known, and uncertainty about its limits. Routine summaries and trimming are workflow-authorized. New intake conversion still requires the explanation and actual permission in [intake](intake.md); reduce usable outputs afterward.

`reduction-save --input <JSON-file>` requires:

- `id`: unique letters/numbers/hyphens/underscores; each revision uses a new ID.
- `source`: workspace-relative usable source file, `source_id`: source identity, `source_reference`: meaningful title/reference.
- `mode`: `text-pages` or `summary`; `pages`: unique positive source page/slide numbers.
- `assessment`: nonempty `basis`, `relevance`, `uncertainty` strings describing size inspection, objective relevance and uncertainty about chatbot limits.
- `critical_details`: list of `{ "detail": "Denominator definition", "evidence": "denominator defines equal parts" }` records for every lesson-critical detail. Each evidence passage must occur in the derivative.
- `omissions`: list disclosing omitted relevant content and its effect; `limitations`: list of fidelity or context gaps. Use empty lists when none apply.

`text-pages` selects UTF-8 pages separated by form-feed characters, numbered from 1, in the requested order (for example `pages: [1, 3]`). For `summary`, also supply `content` with the planner-authored summary and `method` explaining derivation. For PDF/slides, inspect actual pages with document tools and prepare a usable summary; this helper does not trim native PDFs. Inspect actual content or rendering, since filenames do not establish retention.

Compare the derivative against the original and objectives. Verify meaning and completeness of every critical detail; literal passage checks establish only presence. Disclose relevant omissions and their impact. Revise context or teaching scope if a missing detail prevents teaching. The helper records the planner's verification rather than proving semantic completeness.

The operation preserves originals and existing derivatives, writes `materials/derived/reduction-<id>.txt`, and records references, source and derivative digests, method, assessment, evidence and limitations in state. Include the returned `path` in packet `context` with its source reference. Issuance copies actual bytes plus full derivation into the manifest. Changed derivatives require a new verified record. Explain omissions and limitations to the student and lesson chatbot.
