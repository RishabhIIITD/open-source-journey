# Case Study 28: Unindexed Repository Guard for Repowise Coverage Commands

## Executive Summary

| Attribute | Details |
| :--- | :--- |
| **Target Repository** | [`repowise-dev/repowise`](https://github.com/repowise-dev/repowise) |
| **Pull Request** | [PR #6278: fix(coverage): guard coverage add and status against unindexed repositories (#5743)](https://github.com/repowise-dev/repowise/pull/6278) |
| **Issue Resolved** | [Issue #5743: [Bug] coverage add and coverage status crash with a traceback in a repository that was never indexed](https://github.com/repowise-dev/repowise/issues/5743) |
| **Author** | **Rishabh Bafna** (`@RishabhIIITD` / `rishabh20118@iiitd.ac.in`) |
| **Status** | 🟣 Merged (Merged Nov 26, 2026) |
| **Test Verification** | 100% unit tests passing (31 passed, 4 skipped in `tests/unit/cli/test_coverage_cmd.py`) |

---

## 1. Problem Statement

When a user runs `repowise coverage add` or `repowise coverage status` in a repository where `repowise init` / indexing was never executed, the commands crashed with an unhandled exception and full Python traceback (`sqlite3.OperationalError: no such table`).

Like sibling commands (`changes`, `events`, `doctor`), coverage commands must gracefully handle unindexed repositories by printing a user-friendly notice or returning structured JSON errors when `--format json` is passed, exiting with status code 1 without dumping a stack trace.

---

## 2. Technical Implementation

### A. Index Guard Helper in `coverage_cmd.py`

In `packages/cli/src/repowise/cli/commands/coverage_cmd.py`:
- Added database existence check `has_db_store(repo_path)` before attempting queries in `coverage add` and `coverage status`.
- Emitted user notice: `"No index found. Run `repowise init` first."` for human output, or structured JSON `{"error": "No index found. Run repowise init first."}` when `--format json` is requested.
- Gracefully exited with status code `1`.

### B. Unit Test Coverage in `test_coverage_cmd.py`

In `tests/unit/cli/test_coverage_cmd.py`:
- Added test cases verifying both human-readable and `--format json` behaviors when invoked on an empty or unindexed repository directory.

---

## 3. Verification & Results

- Ran `PYTHONPATH=... pytest tests/unit/cli/test_coverage_cmd.py`:
  - **31 passed, 4 skipped, 0 failed**.
- Opened upstream Pull Request [#6278](https://github.com/repowise-dev/repowise/pull/6278).
