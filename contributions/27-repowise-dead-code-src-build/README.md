# Case Study 27: Dead Code Analysis Path Boundary Fix for Shipped src/build Trees

## Executive Summary

| Attribute | Details |
| :--- | :--- |
| **Target Repository** | [`repowise-dev/repowise`](https://github.com/repowise-dev/repowise) |
| **Pull Request** | [PR #6277: fix(dead_code): prevent convention never-flag glob from skipping src/build (#6263)](https://github.com/repowise-dev/repowise/pull/6277) |
| **Issue Resolved** | [Issue #6263: [Bug] The dead-code never-flag glob */build/** still skips shipped src/build files](https://github.com/repowise-dev/repowise/issues/6263) |
| **Author** | **Rishabh Bafna** (`@RishabhIIITD` / `rishabh20118@iiitd.ac.in`) |
| **Status** | 🟢 Open / In Review |
| **Test Verification** | 100% unit tests passing (69/69 in `tests/unit/dead_code/test_convention_never_flag.py`) |

---

## 1. Problem Statement

Repowise dead code analysis maintains a list of "never-flag" patterns to ignore build artifacts and compiled output directories (such as `build/**`, `dist/**`).

In Issue #6263, users reported that production code residing inside `src/build/` (for example, a source build utility module like `src/build/compiler.py`) was erroneously matched by the glob `*/build/**` and exempted from dead code analysis. Because `*/build/**` matched any folder where `build` is preceded by one path component (such as `src`), legitimate source files were skipped.

---

## 2. Technical Implementation

### A. Constraining Never-Flag Globs in `constants.py`

In `packages/core/src/repowise/core/analysis/dead_code/constants.py`:
- Replaced ambiguous wildcards with root-anchored build artifact paths (`build/**`, `.build/**`).
- Ensured nested source directory conventions like `src/build/**` or `packages/*/src/build/**` are preserved for full dead code scanning.

### B. Unit Test Coverage in `test_convention_never_flag.py`

Added unit tests in `tests/unit/dead_code/test_convention_never_flag.py` verifying that:
- Top-level `build/` files remain ignored.
- Files under `src/build/` are properly scanned and analyzed.

---

## 3. Verification & Results

- Ran `PYTHONPATH=... pytest tests/unit/dead_code/test_convention_never_flag.py`:
  - **69 passed, 0 failed**.
- Opened upstream Pull Request [#6277](https://github.com/repowise-dev/repowise/pull/6277).
