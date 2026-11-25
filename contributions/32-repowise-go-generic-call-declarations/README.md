# Case Study 32: Generic Constructor Call Receiver Type Inference for Go

## Executive Summary

| Attribute | Details |
| :--- | :--- |
| **Target Repository** | [`repowise-dev/repowise`](https://github.com/repowise-dev/repowise) |
| **Pull Request** | [PR #6283: fix(ingestion): recognize Go generic constructor call receiver assignments (#2796)](https://github.com/repowise-dev/repowise/pull/6283) |
| **Issue Resolved** | [Issue #2796: A generic constructor call (x := New[T](...)) leaves its local untyped in Go](https://github.com/repowise-dev/repowise/issues/2796) |
| **Author** | **Rishabh Bafna** (`@RishabhIIITD` / `rishabh20118@iiitd.ac.in`) |
| **Status** | 🟢 Open / In Review |
| **Test Verification** | 100% unit tests passing (250/250 in `tests/unit/ingestion/test_receiver_types.py`) |

---

## 1. Problem Statement

Repowise indexes call graphs and type definitions across languages without requiring slow full compiler type-checking passes. In Go, receiver types on local variable assignments (`x := pkg.New(...)`) are resolved using lightweight regex and AST heuristics.

In Issue #2796, when a constructor call employed Go type parameters / generics (e.g. `x := New[T](...)` or `x := pkg.NewSlice[int](...)`), the regex pattern `_CALL_ASSIGNMENT` failed to match because bracketed type arguments `[...]` were not accounted for between the function name and call arguments. As a result, the variable `x` remained untyped, dropping all subsequent method calls on `x` from the call graph.

---

## 2. Technical Implementation

### A. Generic Type Parameter Support in Receiver Types

In `packages/core/src/repowise/core/ingestion/languages/receiver_types.py`:
- Updated `_CALL_ASSIGNMENT` to support optional type arguments `(?:\[[^\]]+\])?` following the constructor or factory function identifier.
- Ensured type arguments are cleanly parsed so the underlying struct/type name is mapped to the variable.

### B. Unit Test Coverage in `test_receiver_types.py`

In `tests/unit/ingestion/test_receiver_types.py`:
- Added test cases verifying that `x := New[T]()`, `x := pkg.NewService[Config]()`, and pointer returns with generics correctly associate `x` with the target receiver type.

---

## 3. Verification & Results

- Ran `PYTHONPATH=... pytest tests/unit/ingestion/test_receiver_types.py`:
  - **250 passed, 0 failed**.
- Opened upstream Pull Request [#6283](https://github.com/repowise-dev/repowise/pull/6283).
