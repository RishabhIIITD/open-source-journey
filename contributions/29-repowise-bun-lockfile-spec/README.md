# Case Study 29: Bun and PDM Lockfile Ingestion Support for Workspace Members

## Executive Summary

| Attribute | Details |
| :--- | :--- |
| **Target Repository** | [`repowise-dev/repowise`](https://github.com/repowise-dev/repowise) |
| **Pull Request** | [PR #6279: fix(specs): include bun and pdm lockfiles in language specifications (#5871)](https://github.com/repowise-dev/repowise/pull/6279) |
| **Issue Resolved** | [Issue #5871: [Bug] A bun workspace member gets npm install in the evidence setup workflow](https://github.com/repowise-dev/repowise/issues/5871) |
| **Author** | **Rishabh Bafna** (`@RishabhIIITD` / `rishabh20118@iiitd.ac.in`) |
| **Status** | 🟢 Open / In Review |
| **Test Verification** | 100% unit tests passing (203/203 in `tests/unit/test_coverage_stacks.py`) |

---

## 1. Problem Statement

Repowise generates automated test and coverage execution stacks for diverse language ecosystems. When analyzing monorepo workspaces, workspace members (e.g. `packages/web`) typically do not possess a local lockfile; instead, their package manager is determined by the nearest governing lockfile discovered up the directory tree.

In Issue #5871, repositories using Bun workspaces with a root `bun.lock` or `bun.lockb` file were misconfigured during CI setup: member packages received `npm install` instead of `bun install --frozen-lockfile`. Investigation revealed that `_lock_dir` relies on `spec.lock_files` from the `javascript` language specification, which only listed `package-lock.json`, `yarn.lock`, and `pnpm-lock.yaml`.

---

## 2. Technical Implementation

### A. Shared Node Lockfiles in Language Specs

In `packages/core/src/repowise/core/ingestion/languages/specs/`:
- In `typescript.py`, defined:
  ```python
  NODE_LOCK_FILES: tuple[str, ...] = (
      "package-lock.json",
      "yarn.lock",
      "pnpm-lock.yaml",
      "bun.lock",
      "bun.lockb",
  )
  ```
- Exported and reused `NODE_LOCK_FILES` across `typescript.py`, `javascript.py`, `vue.py`, and `svelte.py`.
- Added `"pdm.lock"` to `python.py` lockfiles specification.

### B. Unit Test Coverage in `test_coverage_stacks.py`

In `tests/unit/test_coverage_stacks.py`:
- Added `test_a_bun_member_installs_with_bun` verifying that workspace members under both `bun.lock` and `bun.lockb` identify package manager as `bun` and configure `bun install --frozen-lockfile`.

---

## 3. Verification & Results

- Ran `PYTHONPATH=... pytest tests/unit/test_coverage_stacks.py`:
  - **203 passed, 0 failed**.
- Opened upstream Pull Request [#6279](https://github.com/repowise-dev/repowise/pull/6279).
