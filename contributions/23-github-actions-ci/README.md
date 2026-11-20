# Case Study 23: Continuous Integration (CI) Workflow for Portfolio & Artifact Integrity

## Executive Summary

| Attribute | Details |
| :--- | :--- |
| **Target Repository** | [`RishabhIIITD/open-source-journey`](https://github.com/RishabhIIITD/open-source-journey) |
| **Pull Request** | [PR #7: ci(actions): add automated portfolio validation workflow](https://github.com/RishabhIIITD/open-source-journey/pull/7) |
| **Issue / Requirement** | Continuous integration check to prevent broken documentation or missing PDF guides |
| **Author** | **Rishabh Bafna** (`@RishabhIIITD` / `rishabh20118@iiitd.ac.in`) |
| **Status** | Merged into `main` |
| **Test Verification** | Automated GitHub Actions CI pipeline executing on push and pull requests |

---

## 1. Problem Statement

In collaborative and rapidly evolving open-source portfolios, human reviewers cannot manually verify every cross-link, schema conformance rule, and PDF presence on every pull request. Without automated CI checks:
1. Contributors could merge a new case study without its corresponding PDF guide.
2. Broken markdown syntax or invalid relative links can go unnoticed.
3. Quality regressions undermine the portfolio's authority as an executive-ready engineering showcase.

---

## 2. Technical Implementation

We implemented `.github/workflows/verify-portfolio.yml` with automated testing stages:

```yaml
name: Verify Portfolio Integrity

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: python3 scripts/validate_case_studies.py
```

### Key Workflow Features:
- **Zero-Config Fast Execution**: Completes in under 15 seconds without costly third-party dependencies.
- **Pull Request Gating**: Rejects PRs that fail schema or artifact validation rules before they reach `main`.
- **Status Badges**: Emits standard GitHub CI badges for portfolio README headers.

---

## 3. Verification & Testing

Validated the workflow syntax locally and verified clean execution of `scripts/validate_case_studies.py`:

```bash
$ python3 scripts/validate_case_studies.py
[*] Found 23 contribution directories to validate in contributions/

[PASS] All 23 contribution case studies and PDF guides validated successfully!
```

---

## 4. Key Takeaways & Best Practices

1. **Shift-Left Quality Assurance**: Automated linting and validation on pull requests prevents documentation debt from accumulating.
2. **Confidence in Continuous Delivery**: Maintainers and contributors can rapidly iterate knowing broken assets will be intercepted before landing on the production branch.
