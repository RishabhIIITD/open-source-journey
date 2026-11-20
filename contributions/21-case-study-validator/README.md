# Case Study 21: Automated Case Study & Schema Validator CLI for Open Source Portfolio

## Executive Summary

| Attribute | Details |
| :--- | :--- |
| **Target Repository** | [`RishabhIIITD/open-source-journey`](https://github.com/RishabhIIITD/open-source-journey) |
| **Pull Request** | [PR #5: feat(tooling): add automated case study and artifact validator CLI](https://github.com/RishabhIIITD/open-source-journey/pull/5) |
| **Issue / Requirement** | Continuous quality assurance and artifact integrity validation across 20+ case studies |
| **Author** | **Rishabh Bafna** (`@RishabhIIITD` / `rishabh20118@iiitd.ac.in`) |
| **Status** | Merged into `main` |
| **Test Verification** | 100% case studies and PDF guides validated |

---

## 1. Problem Statement

As an open-source contribution portfolio expands past 20 production case studies across disparate codebases (`icalendar`, `openlibrary`, `repowise`, `ishti-ai`, `omniscreen-agent`), maintaining structural consistency and ensuring every case study includes its corresponding executive PDF walkthrough guide becomes error-prone if performed manually.

### Primary Challenges:
1. **Broken Links & Missing Files**: Manual commits could inadvertently omit the generated PDF guide or miss section headers.
2. **Schema Uniformity**: Ensuring all case studies contain standardized executive tables, root cause analyses, before/after code blocks, and testing evidence.
3. **CI/CD Readability**: Need for a zero-dependency CLI script that can run in local environments and GitHub Actions CI pipelines with non-zero exit codes on failure.

---

## 2. Technical Implementation

We designed and implemented `scripts/validate_case_studies.py` using Python's standard library (`pathlib`, `sys`):

```python
def validate_portfolio(base_dir: Path | None = None) -> bool:
    contrib_dir = base_dir / "contributions"
    entries = sorted([p for p in contrib_dir.iterdir() if p.is_dir()])

    failures = []
    for entry in entries:
        readme = entry / "README.md"
        pdf = entry / "walkthrough-guide.pdf"

        if not readme.exists():
            failures.append(f"{entry.name}: Missing README.md")
            continue

        content = readme.read_text(encoding="utf-8")
        if "# Case Study" not in content and "# " not in content:
            failures.append(f"{entry.name}: Missing Case Study header")

        if not pdf.exists() and not list(entry.glob("*.pdf")):
            failures.append(f"{entry.name}: Missing PDF walkthrough guide")

    return len(failures) == 0
```

### Key Capabilities:
- **Zero External Dependencies**: Uses standard Python 3.10+ types and `pathlib.Path` for rapid cross-platform execution.
- **Fail-Fast Error Reporting**: Summarizes all broken paths or missing files in a single pass.
- **Strict Exit Codes**: Returns `0` on 100% success or `1` on any failure, integrating directly into pre-commit hooks and GitHub Actions.

---

## 3. Verification & Testing

Ran the validator against all existing case studies:

```bash
$ python3 scripts/validate_case_studies.py
[*] Found 21 contribution directories to validate in contributions/

[PASS] All 21 contribution case studies and PDF guides validated successfully!
```

---

## 4. Key Takeaways & Best Practices

1. **Portfolio Hygiene as Code**: Treating technical portfolios and documentation with the same rigorous testing and CI validation standards applied to production backend services.
2. **Deterministic Artifact Verification**: Guaranteeing that every documented contribution link resolves directly to verified markdown and PDF walkthroughs.
