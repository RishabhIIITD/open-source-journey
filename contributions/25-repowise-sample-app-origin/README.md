# Case Study 25: Sample and Test App Exclusion in Repowise Code Origin Classification

## Executive Summary

| Attribute | Details |
| :--- | :--- |
| **Target Repository** | [`repowise-dev/repowise`](https://github.com/repowise-dev/repowise) |
| **Pull Request** | [PR #6275: fix(code_origin): treat sample-app, test-app, playground as sample code (#6220)](https://github.com/repowise-dev/repowise/pull/6275) |
| **Issue Resolved** | [Issue #6220: [Bug] path_origin reads sample-app, test-app and playground folders as production code](https://github.com/repowise-dev/repowise/issues/6220) |
| **Author** | **Rishabh Bafna** (`@RishabhIIITD` / `rishabh20118@iiitd.ac.in`) |
| **Status** | 🔴 Closed (Duplicate of #6231) |
| **Test Verification** | 100% unit tests passing (163/163 in `tests/unit/test_code_origin.py`) |

---

## 1. Problem Statement

Repowise classifies codebase paths into operational roles (e.g., `production`, `test`, `sample`, `generated`, `documentation`) using the `path_origin()` function. This classification governs architectural health scores, dead code analysis, and dependency audits.

In Issue #6220, users observed that directories such as `sample-app`, `test-app`, `e2e-app`, and `playground` were being misclassified as `production` code. This happened because token matching only looked for exact component matches (`sample`, `test`, `example`) and did not inspect hyphen-separated sub-tokens (e.g. `sample-app`), or missed dedicated directory names like `playground`. As a result, non-production demo applications and playgrounds were counted towards production architecture and dead code audits.

---

## 2. Technical Implementation

### A. Token Splitting and Rule Expansion in `code_origin.py`

In `packages/core/src/repowise/core/code_origin.py`:
- Updated token extraction logic so hyphen-delimited directory names (e.g. `sample-app`, `test-app`, `demo-project`) are parsed into constituent semantic tokens.
- Added `playground` to the recognized sample directory tokens.
- Mapped tokens such as `sample-app`, `test-app`, and `playground` to return `CodeOrigin.SAMPLE` or `CodeOrigin.TEST` appropriately.

```python
# Expanded sample and test directory detection
SAMPLE_DIR_NAMES = frozenset({"sample", "samples", "example", "examples", "playground", "demo", "demos"})
```

### B. Unit Test Expansion

In `tests/unit/test_code_origin.py`:
- Added test cases asserting that paths containing `sample-app/`, `test-app/`, and `playground/` classify as non-production code origins.

---

## 3. Verification & Results

- Ran `PYTHONPATH=packages/core/src pytest tests/unit/test_code_origin.py -k test_path_rules`:
  - **163 passed, 0 failed**.
- Opened upstream Pull Request [#6275](https://github.com/repowise-dev/repowise/pull/6275).
