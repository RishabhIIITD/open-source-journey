# Case Study 25: RFC Reference Dictionary & Cross-Protocol Technical Index

## Executive Summary

| Attribute | Details |
| :--- | :--- |
| **Target Repository** | [`RishabhIIITD/open-source-journey`](https://github.com/RishabhIIITD/open-source-journey) |
| **Pull Request** | [PR #9: docs: add RFC 5545 reference dictionary and telemetry technical index](https://github.com/RishabhIIITD/open-source-journey/pull/9) |
| **Issue / Requirement** | Structured technical definitions for RFC 5545 recurrence rules and distributed telemetry protocols |
| **Author** | **Rishabh Bafna** (`@RishabhIIITD` / `rishabh20118@iiitd.ac.in`) |
| **Status** | Merged into `main` |
| **Test Verification** | RFC cross-references and documentation validation passing |

---

## 1. Problem Statement

Across the 20+ production open-source contributions in this repository, many changes implement granular parts of standard specifications (RFC 5545, RFC 7529, SQLite WAL journaling, Docker OCI image manifests). Without a unified technical dictionary, readers and interviewers reviewing specific case studies lack immediate context on standard syntax and edge-case behavior.

### Objective:
Curate a dedicated **RFC Reference Dictionary** (`docs/RFC_GLOSSARY.md`) documenting all recurrence properties, frequency constraints, non-Gregorian extensions, and database telemetry primitives referenced across our open-source patches.

---

## 2. Technical Implementation

Authored `docs/RFC_GLOSSARY.md` containing:
1. **RFC 5545 iCalendar Standards**: Detailed reference tables for `VEVENT`, `VTODO`, `VJOURNAL`, and `VTIMEZONE`.
2. **Algorithmic Recurrence Attributes**: Complete breakdown of `BYDAY`, `BYMONTHDAY`, `BYWEEKNO`, `BYYEARDAY`, `BYSETPOS`, and ordinal day prefixes.
3. **RFC 7529 Extensions**: Explaining `RSCALE` (Hebrew, Islamic, Ethiopic calendar systems) and `SKIP` leap-date handling (`OMIT`, `BACKWARD`, `FORWARD`).
4. **SQLite Concurrency & WAL Mechanics**: Explaining Write-Ahead Logging, `PRAGMA synchronous = NORMAL`, and `busy_timeout` locking semantics.

---

## 3. Verification & Testing

Validated document structure, cross-references, and verified schema compliance with `scripts/validate_case_studies.py`:

```bash
$ python3 scripts/validate_case_studies.py
[*] Found 25 contribution directories to validate in contributions/

[PASS] All 25 contribution case studies and PDF guides validated successfully!
```

---

## 4. Key Takeaways & Best Practices

1. **Standards-Driven Engineering**: Building systems against formal RFC specifications guarantees interoperability across enterprise calendar servers (Google Calendar, Apple iCal, Outlook).
2. **Context-Rich Documentation**: Supplementing code case studies with a shared technical glossary accelerates onboarding and deepens technical credibility.
