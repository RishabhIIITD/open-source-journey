# Case Study 31: Language Tail Preservation in Paired Test File Basenames

## Executive Summary

| Attribute | Details |
| :--- | :--- |
| **Target Repository** | [`repowise-dev/repowise`](https://github.com/repowise-dev/repowise) |
| **Pull Request** | [PR #6282: fix(health): preserve language suffixes in paired test basenames (#5697)](https://github.com/repowise-dev/repowise/pull/6282) |
| **Issue Resolved** | [Issue #5697: [Bug] A test is credited to a same-named file in an unrelated package](https://github.com/repowise-dev/repowise/issues/5697) |
| **Author** | **Rishabh Bafna** (`@RishabhIIITD` / `rishabh20118@iiitd.ac.in`) |
| **Status** | 🟢 Open / In Review |
| **Test Verification** | 100% unit tests passing (70/70 across `test_paired_test_basenames.py` and `test_test_reachability.py`) |

---

## 1. Problem Statement

Repowise pairs test files with production implementation files across diverse repository architectures to calculate reachability, test impact, and code health.

In Issue #5697, when stripping conventional test affixes from file basenames, `test_paths.py` stripped the compound suffix (such as `.spec.ts` -> `file`) but discarded directory path tokens and language extensions prematurely. Consequently, a test in one package (e.g. `packages/ui/test/utils.spec.ts`) was falsely credited to an identically named file in an unrelated package (e.g. `packages/core/src/utils.py`).

---

## 2. Technical Implementation

### A. Context-Aware Test Basename Stripping

In `packages/core/src/repowise/core/test_paths.py`:
- Refined `paired_test_basenames` to preserve language extensions and respect path hierarchies when resolving candidates.
- Prevented cross-ecosystem collisions by retaining language affinity during test-to-implementation pairing.

### B. Unit Test Coverage

In `tests/unit/health/test_paired_test_basenames.py`:
- Added test cases verifying that same-named files in separate packages and different languages are not erroneously paired.

---

## 3. Verification & Results

- Ran `PYTHONPATH=... pytest tests/unit/health/test_paired_test_basenames.py tests/unit/analysis/test_test_reachability.py`:
  - **70 passed, 0 failed**.
- Opened upstream Pull Request [#6282](https://github.com/repowise-dev/repowise/pull/6282).
