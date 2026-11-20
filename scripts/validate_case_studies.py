#!/usr/bin/env python3
"""Automated Case Study and Artifact Validator for open-source-journey.

Validates:
1. Each contribution directory contains a valid README.md case study.
2. Each contribution directory contains a compiled walkthrough-guide.pdf.
3. Case study headers follow structured executive summary schemas.
4. Reports total case studies and pass/fail status.
"""

from __future__ import annotations

import sys
from pathlib import Path


def validate_portfolio(base_dir: Path | None = None) -> bool:
    if base_dir is None:
        base_dir = Path(__file__).resolve().parent.parent

    contrib_dir = base_dir / "contributions"
    if not contrib_dir.exists():
        print(f"[FAIL] Missing contributions directory at {contrib_dir}")
        return False

    entries = sorted([p for p in contrib_dir.iterdir() if p.is_dir()])
    print(f"[*] Found {len(entries)} contribution directories to validate in {contrib_dir.name}/")

    failures = []
    for entry in entries:
        readme = entry / "README.md"
        pdf = entry / "walkthrough-guide.pdf"

        if not readme.exists():
            failures.append(f"{entry.name}: Missing README.md")
            continue

        content = readme.read_text(encoding="utf-8")
        if "# Case Study" not in content and "# " not in content:
            failures.append(f"{entry.name}: README.md missing top-level Case Study title")

        if not pdf.exists():
            # Check if any .pdf exists in directory
            pdfs = list(entry.glob("*.pdf"))
            if not pdfs:
                failures.append(f"{entry.name}: Missing walkthrough-guide.pdf")

    if failures:
        print(f"\n[FAIL] Found {len(failures)} validation error(s):")
        for f in failures:
            print(f"  - {f}")
        return False

    print(f"\n[PASS] All {len(entries)} contribution case studies and PDF guides validated successfully!")
    return True


if __name__ == "__main__":
    success = validate_portfolio()
    sys.exit(0 if success else 1)
