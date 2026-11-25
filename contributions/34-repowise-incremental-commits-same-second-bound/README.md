# Case Study 34: Boundary Commit Timestamp Capture for Incremental Update Ingestion

## Executive Summary

| Attribute | Details |
| :--- | :--- |
| **Target Repository** | [`repowise-dev/repowise`](https://github.com/repowise-dev/repowise) |
| **Pull Request** | [PR #6285: fix(ingestion): include same-second commits at since_ts boundary (#6150)](https://github.com/repowise-dev/repowise/pull/6285) |
| **Issue Resolved** | [Issue #6150: [Bug] Incremental update drops same-second commits and non-monotonic DAG commits due to strict timestamp inequality](https://github.com/repowise-dev/repowise/issues/6150) |
| **Author** | **Rishabh Bafna** (`@RishabhIIITD` / `rishabh20118@iiitd.ac.in`) |
| **Status** | 🟢 Open / In Review |
| **Test Verification** | 100% unit tests passing (21/21 in `tests/unit/test_git_commit_rows.py` and `test_git_commit_index.py`) |

---

## 1. Problem Statement

Repowise tracks commit histories incrementally during `repowise update` to avoid re-walking entire repositories. The incremental pipeline stores the latest commit timestamp (`since_ts`) and requests only commits newer than that boundary from git.

In Issue #6150, `_stamp_after` and `_commits_after` in `git_commit_index.py` used strict inequality (`> since_ts`). When multiple commits occurred within the same second (e.g. automated CI commits, squash/rebase merges) matching the stored boundary timestamp, or branch commits had timestamps equal to `since_ts`, they were permanently discarded.

---

## 2. Technical Implementation

### A. Boundary Timestamp Inclusivity

In `packages/core/src/repowise/core/ingestion/git_commit_index.py`:
- Updated `_stamp_after` to test `int(stamp) >= since_ts` so same-second commits are preserved in the shallow window depth calculation.
- Updated `_commits_after` to yield records matching `parsed[0]["ts"] >= since_ts`.
- Ingestion deduplication on SHA ensures re-evaluating boundary commits is idempotent and completely safe.

### B. Unit Test Coverage in `test_git_commit_rows.py`

In `tests/unit/test_git_commit_rows.py`:
- Added `test_since_ts_captures_same_second_commits` verifying that commits sharing the boundary timestamp `since_ts` are captured and not dropped.

---

## 3. Verification & Results

- Ran `PYTHONPATH=... pytest tests/unit/test_git_commit_rows.py tests/unit/test_git_commit_index.py`:
  - **21 passed, 0 failed**.
- Opened upstream Pull Request [#6285](https://github.com/repowise-dev/repowise/pull/6285).
