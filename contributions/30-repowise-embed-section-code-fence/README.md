# Case Study 30: Code Fence Boundary Isolation in Markdown Section Extraction

## Executive Summary

| Attribute | Details |
| :--- | :--- |
| **Target Repository** | [`repowise-dev/repowise`](https://github.com/repowise-dev/repowise) |
| **Pull Request** | [PR #6281: fix(generation): handle markdown headings within code fences in embed_section (#5357)](https://github.com/repowise-dev/repowise/pull/6281) |
| **Issue Resolved** | [Issue #5357: [Bug] embed_section treats a "## heading" inside a code fence as the end of the section](https://github.com/repowise-dev/repowise/issues/5357) |
| **Author** | **Rishabh Bafna** (`@RishabhIIITD` / `rishabh20118@iiitd.ac.in`) |
| **Status** | 🟢 Open / In Review |
| **Test Verification** | 100% unit tests passing (15/15 in `tests/unit/generation/test_model_page_shape.py`) |

---

## 1. Problem Statement

Repowise generates structured markdown architecture and overview pages for code repositories. The `embed_section` helper parses source markdown documents to extract specific sections bounded by markdown headings (e.g., `## Heading`).

In Issue #5357, when a target section contained fenced code blocks with markdown snippets inside (such as sample markdown documentation with `## Example`), `embed_section` prematurely truncated the section at the first embedded `##` line inside the code fence. This led to broken code examples and incomplete page rendering.

---

## 2. Technical Implementation

### A. State Tracking for Code Fences

In `packages/core/src/repowise/core/generation/overview_tables.py`:
- Updated `embed_section` to maintain a boolean state tracking whether the cursor is currently inside a code fence (``` or ~~~).
- Ensured heading tokens (lines starting with `#`) inside active code fences do not trigger section termination.

### B. Unit Test Coverage in `test_model_page_shape.py`

In `tests/unit/generation/test_model_page_shape.py`:
- Added `test_embed_section_ignores_headings_inside_code_fences` asserting that markdown headings enclosed within backtick or tilde code fences are preserved without terminating the extracted section.

---

## 3. Verification & Results

- Ran `PYTHONPATH=... pytest tests/unit/generation/test_model_page_shape.py`:
  - **15 passed, 0 failed**.
- Opened upstream Pull Request [#6281](https://github.com/repowise-dev/repowise/pull/6281).
