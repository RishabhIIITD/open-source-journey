# Case Study 33: Multi-Language Coverage Stack Detection for Swift, Dart, and Scala

## Executive Summary

| Attribute | Details |
| :--- | :--- |
| **Target Repository** | [`repowise-dev/repowise`](https://github.com/repowise-dev/repowise) |
| **Pull Request** | [PR #6284: fix(coverage): recognize swift, dart, and scala test runner stacks (#5838)](https://github.com/repowise-dev/repowise/pull/6284) |
| **Issue Resolved** | [Issue #5838: [Bug] Coverage stack detection omits Swift, Dart, and Scala, falling through to UNKNOWN in evidence setup](https://github.com/repowise-dev/repowise/issues/5838) |
| **Author** | **Rishabh Bafna** (`@RishabhIIITD` / `rishabh20118@iiitd.ac.in`) |
| **Status** | 🟢 Rebased & Ready to Merge (Maintainer Review Addressed) |
| **Test Verification** | 100% unit tests passing (244/244 across `test_coverage_stacks.py` and `test_ci_snippet.py`) |

---

## 1. Problem Statement

Repowise provides `repowise evidence setup` and `detect_repo_stacks` to automatically discover how repositories execute tests and measure code coverage across various languages.

In Issue #5838, while Swift (`Package.swift`), Dart (`pubspec.yaml`), and Scala (`build.sbt`) were fully supported in Repowise's language registry for AST and call-graph indexing, they were missing from `_LANGUAGE_STACKS` and `_BUILDERS` in `test_runners/stacks.py`. Consequently, running evidence setup in repositories of these languages resulted in `UNKNOWN` ("Repowise could not tell how this repository runs its tests").

---

## 2. Technical Implementation & Maintainer Feedback Resolution

### A. Coverage Stack Definitions & Builders

In `packages/core/src/repowise/core/test_runners/stacks.py`:
- Added stack builders:
  - `_swift`: runner `swift test`, setup `- uses: swiftlang/setup-swift@v1`, test command `swift test --enable-code-coverage`, report `.build/debug/codecov/*.json`.
  - `_dart`: runner `dart test`, setup `- uses: dart-lang/setup-dart@v1`, prepare `dart pub global activate coverage`, test command `dart test --coverage=coverage && dart pub global run coverage:format_coverage --lcov --in=coverage --out=coverage/lcov.info --packages=.dart_tool/package_config.json --report-on=lib`, report `coverage/lcov.info`.
  - `_scala`: runner `sbt test`, setup `actions/setup-java@v4` with `cache: sbt`, test command `sbt coverage test coverageReport`, report `target/scala-*/scoverage-report/scoverage.xml`.
- Mapped `"swift"`, `"dart"`, and `"scala"` in `_LANGUAGE_STACKS`, `_ORDER`, and `_BUILDERS`.

### B. CI Workflow Generation & Container Mappings

In `packages/core/src/repowise/core/evidence/ci_snippet.py`:
- Maintained maintainer feedback regarding toolchains and non-alpine images:
  - `_GITLAB_IMAGES`: Added explicit container images (`swift:5.10`, `dart:stable`, `sbtscala/scala-sbt:eclipse-temurin-21_1.10.0_3.4.2`).
  - `_GITLAB_TOOLS`: Added `dart` tool installation (`dart pub global activate coverage`).

### C. Unit Test Coverage & Rebase

In `tests/unit/test_coverage_stacks.py` and `tests/unit/evidence/test_ci_snippet.py`:
- Added parameterized unit test `test_new_coverage_stacks_carry_ci_toolchain_and_non_alpine_image` verifying toolchains and non-alpine images for Swift, Dart, and Scala.
- Rebased cleanly onto `upstream/main`, resolving merge conflicts in `tests/unit/test_coverage_stacks.py`.

---

## 3. Verification & Results

- Ran `PYTHONPATH=packages/core/src:packages/cli/src:packages/server/src pytest tests/unit/evidence/test_ci_snippet.py tests/unit/test_coverage_stacks.py`:
  - **244 passed, 0 failed**.
- Maintained feedback addressed and pushed to PR [#6284](https://github.com/repowise-dev/repowise/pull/6284).
