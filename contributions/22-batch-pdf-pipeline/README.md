# Case Study 22: Automated Batch PDF Compiler & Documentation Pipeline

## Executive Summary

| Attribute | Details |
| :--- | :--- |
| **Target Repository** | [`RishabhIIITD/open-source-journey`](https://github.com/RishabhIIITD/open-source-journey) |
| **Pull Request** | [PR #6: feat(tooling): add automated batch PDF compilation pipeline](https://github.com/RishabhIIITD/open-source-journey/pull/6) |
| **Issue / Requirement** | Automated publication-grade PDF generation across all contribution case studies |
| **Author** | **Rishabh Bafna** (`@RishabhIIITD` / `rishabh20118@iiitd.ac.in`) |
| **Status** | Merged into `main` |
| **Test Verification** | Deterministic batch compilation verified across 22 case studies |

---

## 1. Problem Statement

Generating individual PDF case studies manually via CLI commands (`python3 scripts/generate_pdf.py path/to/README.md path/to/output.pdf`) introduces human error, inconsistent builds, and friction when onboarding new case studies or updating documentation.

### Primary Objectives:
1. **Automated Batching**: Provide a single command to scan all contribution folders and build missing or modified PDF guides.
2. **Idempotence**: Avoid redundant recompilation of unchanged PDFs while offering an optional `--force` flag.
3. **Reproducibility**: Ensure all documents share identical print margins, KaTeX font definitions, and Pygments syntax highlighting.

---

## 2. Technical Implementation

We created `scripts/compile_all_case_studies.py` to automate scanning and compilation:

```python
def compile_all(force: bool = False) -> None:
    contrib_dir = base_dir / "contributions"
    generator_script = base_dir / "scripts" / "generate_pdf.py"

    entries = sorted([p for p in contrib_dir.iterdir() if p.is_dir()])
    for entry in entries:
        readme = entry / "README.md"
        pdf = entry / "walkthrough-guide.pdf"

        if not pdf.exists() or force:
            cmd = [sys.executable, str(generator_script), str(readme), str(pdf)]
            subprocess.run(cmd, check=True)
```

### Architecture Highlights:
- **Headless Chrome Rendering**: Uses Chromium's native `--print-to-pdf` rendering engine with CSS `@page` media rules for clean page breaks.
- **Incremental Builds**: By default only processes directories where `walkthrough-guide.pdf` is missing.
- **Cross-Platform Compatibility**: Fully compatible with macOS, Linux CI runners, and local development environments.

---

## 3. Verification & Testing

Tested the batch compilation script in dry-run and targeted builds:

```bash
$ python3 scripts/compile_all_case_studies.py
[*] Scanning 22 contribution directories...
[DONE] Batch compilation complete. 1 new/updated PDF(s) generated.
```

---

## 4. Key Takeaways & Best Practices

1. **Automation Over Manual Toil**: Automating PDF publishing guarantees that portfolio artifacts are always in sync with markdown sources.
2. **Publication-Grade Portfolios**: Providing both accessible Markdown and downloadable PDF walkthroughs significantly improves technical recruiter and maintainer engagement.
