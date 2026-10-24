# 06: Reduce oversized lesson context with traceable derivatives

**What to build:** When lesson context is oversized or excessively extraneous, packet preparation creates usable summaries or trimmed materials while preserving lesson-critical information and traceability.

**Blocked by:** 05: Issue and manage one self-contained lesson packet.

**Status:** resolved

- [x] The planning agent assesses size and relevance for the target chatbot, documents its basis and uncertainty, and selects summaries or trimmed derivatives when appropriate without assuming exact chatbot limits.
- [x] Routine packet summaries and trimming proceed under workflow authorization. New intake conversions still follow the earlier conversion-permission requirement.
- [x] Originals remain unchanged. Derivatives and issued packets record source identity, page or slide references, included content, derivation provenance, and material limitations.
- [x] Preparation verifies that reduced context retains lesson-critical details. Relevant omissions are disclosed rather than silently dropped.
- [x] Issuance preserves the actual derivative files used by the lesson chatbot, so later regeneration cannot silently change the issued snapshot.
- [x] Synthetic public-operation checks use source pages with identifiable content to verify retention, source references, original preservation, and omission reporting. Selected-page PDF checks inspect actual page content or rendering where practical rather than filenames alone.

## Answer

Implemented reduction-save with text-page trimming and planner-authored summaries, explicit size/relevance assessment, source references and hashes, retained evidence checks, and disclosed omissions. Issued manifests snapshot full provenance and derivative bytes. See skill/invo-assignment/references/reductions.md and tests/test_reductions.py. Native PDF trimming is delegated to document tools; helper supports text pages and summaries.

Validation: public CLI retention/snapshot test failed before implementation; all 10 synthetic public CLI tests pass via python -m unittest discover -v.

