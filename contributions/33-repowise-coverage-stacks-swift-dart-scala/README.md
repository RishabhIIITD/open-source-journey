# Case Study 33: Multi-Language Coverage Stack Detection for Swift, Dart, and Scala

## Executive Summary

| Attribute | Details |
| :--- | :--- |
| **Target Repository** | [`repowise-dev/repowise`](https://github.com/repowise-dev/repowise) |
| **Pull Request** | [PR #6284: fix(coverage): recognize swift, dart, and scala test runner stacks (#5838)](https://github.com/repowise-dev/repowise/pull/6284) |
| **Issue Resolved** | [Issue #5838: [Bug] Coverage stack detection omits Swift, Dart, and Scala, falling through to UNKNOWN in evidence setup](https://github.com/repowise-dev/repowise/issues/5838) |
| **Author** | **Rishabh Bafna** (`@RishabhIIITD` / `rishabh20118@iiitd.ac.in`) |
| **Status** | 🟢 Open / In Review |
| **Test Verification** | 100% unit tests passing (205/205 in `tests/unit/test_coverage_stacks.py`) |

---

## 1. Problem Statement

Repowise provides `repowise evidence setup` and `detect_repo_stacks` to automatically discover how repositories execute tests and measure code coverage across various languages.

In Issue #5838, while Swift (`Package.swift`), Dart (`pubspec.yaml`), and Scala (`build.sbt`) were fully supported in Repowise's language registry for AST and call-graph indexing, they were missing from `_LANGUAGE_STACKS` and `_BUILDERS` in `test_runners/stacks.py`. Consequently, running evidence setup in repositories of these languages resulted in `UNKNOWN` ("Repowise could not tell how this repository runs its tests").

---

## 2. Technical Implementation

### A. Coverage Stack Definitions & Builders

In `packages/core/src/repowise/core/test_runners/stacks.py`:
- Added stack builders:
  - `_swift`: runner `swift test`, test command `swift test --enable-code-coverage`, report `.build/debug/codecov/*.json`.
  - `_dart`: runner `dart test`, test command `dart test --coverage=coverage`, report `coverage/lcov.info`.
  - `_scala`: runner `sbt test`, test command `sbt coverage test coverageReport`, report `target/scala-*/scoverage-report/scoverage.xml`.
- Mapped `"swift"`, `"dart"`, and `"scala"` in `_LANGUAGE_STACKS`, `_ORDER`, and `_BUILDERS`.

### B. Unit Test Coverage in `test_coverage_stacks.py`

In `tests/unit/test_coverage_stacks.py`:
- Added tests `test_swift_repository_yields_swift_stack`, `test_dart_repository_yields_dart_stack`, and `test_scala_repository_yields_scala_stack` verifying end-to-end detection.

---

## 3. Verification & Results

- Ran `PYTHONPATH=... pytest tests/unit/test_coverage_stacks.py`:
  - **205 passed, 0 failed**.
- Opened upstream Pull Request [#6284](https://github.com/repowise-dev/repowise/pull/6284).
