#!/usr/bin/env python3
"""High-fidelity PDF generator for Open Source Journey Case Studies.

Converts Markdown case studies into executive-ready, publication-grade PDFs
using Python-Markdown (with tables, codehilite, fenced_code), Pygments styling,
and headless Google Chrome with strict print stylesheets.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import markdown
from pygments.formatters import HtmlFormatter

PYGMENTS_CSS = HtmlFormatter(style="friendly").get_style_defs(".codehilite")

DOCUMENT_CSS = f"""
@page {{
    size: A4;
    margin: 18mm 16mm 20mm 16mm;
    @top-right {{
        content: "Open Source Portfolio | Rishabh Bafna";
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-size: 8pt;
        color: #94a3b8;
    }}
    @bottom-center {{
        content: counter(page);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-size: 9pt;
        color: #64748b;
    }}
}}

*, *::before, *::after {{
    box-sizing: border-box;
}}

body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Inter", Helvetica, Arial, sans-serif;
    font-size: 10.5pt;
    line-height: 1.65;
    color: #1e293b;
    background-color: #ffffff;
    margin: 0;
    padding: 0;
    text-rendering: optimizeLegibility;
    -webkit-font-smoothing: antialiased;
}}

/* Header Banner */
.doc-header {{
    border-bottom: 2px solid #3b82f6;
    padding-bottom: 12px;
    margin-bottom: 24px;
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
}}

.doc-header .badge {{
    font-size: 8pt;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #2563eb;
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    padding: 3px 8px;
    border-radius: 4px;
}}

.doc-header .contributor {{
    font-size: 8.5pt;
    color: #64748b;
}}

/* Headings */
h1 {{
    font-size: 20pt;
    font-weight: 800;
    line-height: 1.25;
    color: #0f172a;
    margin-top: 0;
    margin-bottom: 16px;
    letter-spacing: -0.02em;
    break-after: avoid;
    page-break-after: avoid;
}}

h2 {{
    font-size: 14pt;
    font-weight: 700;
    color: #0f172a;
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 6px;
    margin-top: 28px;
    margin-bottom: 14px;
    letter-spacing: -0.01em;
    break-after: avoid;
    page-break-after: avoid;
}}

h3 {{
    font-size: 11.5pt;
    font-weight: 600;
    color: #334155;
    margin-top: 20px;
    margin-bottom: 10px;
    break-after: avoid;
    page-break-after: avoid;
}}

p {{
    margin-top: 0;
    margin-bottom: 12px;
    color: #334155;
}}

/* Tables */
table {{
    width: 100%;
    border-collapse: collapse;
    margin: 18px 0 24px 0;
    font-size: 9.5pt;
    page-break-inside: avoid;
    border-radius: 6px;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    border: 1px solid #cbd5e1;
}}

thead {{
    background-color: #0f172a;
    color: #ffffff;
}}

thead th {{
    font-weight: 600;
    text-align: left;
    padding: 10px 14px;
    color: #ffffff;
    font-size: 9pt;
    letter-spacing: 0.03em;
    border-bottom: 1px solid #0f172a;
}}

tbody tr {{
    border-bottom: 1px solid #e2e8f0;
}}

tbody tr:nth-child(even) {{
    background-color: #f8fafc;
}}

tbody tr:hover {{
    background-color: #f1f5f9;
}}

td {{
    padding: 9px 14px;
    color: #334155;
    vertical-align: top;
}}

td strong {{
    color: #0f172a;
}}

/* Links */
a {{
    color: #2563eb;
    text-decoration: none;
    font-weight: 500;
}}

a:hover {{
    text-decoration: underline;
}}

/* Code & Pre */
code {{
    font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
    font-size: 8.8pt;
    background-color: #f1f5f9;
    color: #0f172a;
    padding: 2px 5px;
    border-radius: 4px;
    border: 1px solid #e2e8f0;
}}

pre {{
    font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
    font-size: 8.5pt;
    line-height: 1.5;
    background-color: #f8fafc;
    border: 1px solid #e2e8f0;
    border-left: 3px solid #3b82f6;
    padding: 14px 16px;
    border-radius: 6px;
    overflow-x: auto;
    page-break-inside: avoid;
    margin: 16px 0 20px 0;
}}

pre code {{
    background: none;
    padding: 0;
    border: none;
    font-size: inherit;
    color: inherit;
}}

/* Lists */
ul, ol {{
    margin-top: 4px;
    margin-bottom: 14px;
    padding-left: 22px;
}}

li {{
    margin-bottom: 6px;
    color: #334155;
}}

li strong {{
    color: #0f172a;
}}

/* Blockquotes & Callouts */
blockquote {{
    margin: 16px 0;
    padding: 12px 18px;
    background-color: #f0fdf4;
    border-left: 4px solid #22c55e;
    border-radius: 0 6px 6px 0;
    color: #166534;
    page-break-inside: avoid;
}}

blockquote p {{
    margin: 0;
    color: inherit;
}}

hr {{
    border: none;
    border-top: 1px solid #e2e8f0;
    margin: 28px 0;
}}

/* Syntax Highlighting overrides */
{PYGMENTS_CSS}

.codehilite {{
    background-color: #f8fafc !important;
    border: 1px solid #e2e8f0;
    border-left: 3px solid #3b82f6;
    border-radius: 6px;
    padding: 12px 16px;
    margin: 16px 0 20px 0;
    page-break-inside: avoid;
}}

.codehilite pre {{
    background: none !important;
    border: none !important;
    padding: 0 !important;
    margin: 0 !important;
}}
"""


def compile_markdown_to_pdf(md_path: str | Path, pdf_path: str | Path) -> None:
    md_file = Path(md_path)
    pdf_file = Path(pdf_path)

    text = md_file.read_text(encoding="utf-8")

    # Render with Python-Markdown
    md = markdown.Markdown(
        extensions=[
            "tables",
            "fenced_code",
            "codehilite",
            "toc",
            "sane_lists",
        ],
        extension_configs={
            "codehilite": {
                "css_class": "codehilite",
                "linenums": False,
                "guess_lang": False,
            }
        },
    )

    body_html = md.convert(text)

    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{md_file.parent.name}</title>
<style>
{DOCUMENT_CSS}
</style>
</head>
<body>
<div class="doc-header">
    <span class="badge">Open Source Contribution</span>
    <span class="contributor">Contributor: <strong>Rishabh Bafna</strong> (&lt;rishabh20118@iiitd.ac.in&gt;)</span>
</div>
{body_html}
</body>
</html>
"""

    tmp_html = f"/tmp/{md_file.parent.name}.html"
    Path(tmp_html).write_text(full_html, encoding="utf-8")

    chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    cmd = [
        chrome,
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_file.resolve()}",
        tmp_html,
    ]
    subprocess.run(cmd, check=True)
    print(f"Compiled: {pdf_file.resolve()} ({pdf_file.stat().st_size} bytes)")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: generate_pdf.py <input.md> <output.pdf>")
        sys.exit(1)
    compile_markdown_to_pdf(sys.argv[1], sys.argv[2])
