#!/usr/bin/env python3
"""Batch PDF Compilation Pipeline for open-source-journey.

Scans the contributions directory and compiles any markdown case studies
into high-fidelity PDFs using scripts/generate_pdf.py.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def compile_all(force: bool = False) -> None:
    base_dir = Path(__file__).resolve().parent.parent
    contrib_dir = base_dir / "contributions"
    generator_script = base_dir / "scripts" / "generate_pdf.py"

    if not generator_script.exists():
        print(f"[FAIL] Missing PDF generator at {generator_script}")
        sys.exit(1)

    entries = sorted([p for p in contrib_dir.iterdir() if p.is_dir()])
    print(f"[*] Scanning {len(entries)} contribution directories...")

    compiled = 0
    for entry in entries:
        readme = entry / "README.md"
        pdf = entry / "walkthrough-guide.pdf"

        if not readme.exists():
            continue

        if not pdf.exists() or force:
            print(f"[*] Compiling {entry.name}...")
            cmd = [sys.executable, str(generator_script), str(readme), str(pdf)]
            try:
                subprocess.run(cmd, check=True)
                compiled += 1
            except subprocess.CalledProcessError as e:
                print(f"[ERROR] Failed to compile {entry.name}: {e}")

    print(f"[DONE] Batch compilation complete. {compiled} new/updated PDF(s) generated.")


if __name__ == "__main__":
    force_rebuild = "--force" in sys.argv
    compile_all(force=force_rebuild)
