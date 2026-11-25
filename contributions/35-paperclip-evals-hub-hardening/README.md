# Case Study 35: Hardening Date Parsing, Path Traversal Protection, and UTF-8 Encoding in Evals Hub

## Executive Summary

| Attribute | Details |
| :--- | :--- |
| **Target Repository** | [`paperclipai/paperclip`](https://github.com/paperclipai/paperclip) |
| **Pull Request** | [PR #22903: fix(evals-hub): harden date parsing, url traversal guards and utf-8 encoding](https://github.com/paperclipai/paperclip/pull/22903) |
| **Issue Resolved** | In-PR Bug Report & Greptile Security Review: Evals hub script lacks explicit UTF-8 encoding, rejects RFC 3339 lowercase timestamps, omits encoded URL path traversal checks, and raises unhandled KeyErrors |
| **Author** | **Rishabh Bafna** (`@RishabhIIITD` / `rishabh20118@iiitd.ac.in`) |
| **Status** | 🟢 Open / In Review |
| **Test Verification** | 100% unit tests passing (16/16 across `scripts/evals-hub/test_build.py` and `tests/runner-e2e/test_evals_hub_build.py`) |

---

## 1. Problem Statement

Paperclip is the open-source platform used to orchestrate and manage AI agent fleets. As part of its automated evaluation and quality assurance pipelines, `scripts/evals-hub/build.py` builds the public evaluations directory and summary index from runner protocol evaluation feeds and end-to-end campaign logs.

During an audit of the Python tooling and build pipeline:
1. **Implicit Locale Encoding in File I/O**: `read_text()` and `write_text()` in `build.py` omitted explicit `encoding="utf-8"`. On non-UTF-8 host locales (e.g., Windows environments defaulting to CP1252 or minimal Linux containers with `LANG=C`), parsing and rendering templates containing Unicode characters (such as the middle dot `·` in `display_date`) crashes with `UnicodeDecodeError` or `UnicodeEncodeError`.
2. **Naive Timestamp Normalization**: `display_date(value)` used a naive `value.replace("Z", "+00:00")`. This failed on valid RFC 3339 timestamps using lowercase `z` or timestamps with surrounding whitespace, and performed a global replacement rather than strictly stripping the trailing UTC designator.
3. **URL Path Traversal Risk (Direct & URL-Encoded)**: `public_report(url, prefix)` verified that URLs started with `/{prefix}/campaigns/` but failed to reject `/../` directory traversal sequences, URL-encoded parent directories (`%2e%2e`), or backslashes (`\`) which browsers resolve as path separators, allowing malicious or malformed report URLs to escape the campaign directory.
4. **Unhandled KeyErrors on Malformed Campaign Feeds**: In `latest()` and `summarize()`, missing keys such as `campaigns` or `totals["passed"]` raised raw `KeyError` or `TypeError` rather than descriptive `ValueError` exceptions expected by callers.

---

## 2. Technical Implementation

### A. Explicit UTF-8 Encoding & Path Safety

In `scripts/evals-hub/build.py`:
- Added `encoding="utf-8"` to all `read_text()` and `write_text()` invocations in `main()`.
- Enhanced `public_report()` with explicit string type verification, URL-decoding (`unquote()`), backslash normalization, and `posixpath.normpath()` path traversal guards:

```python
def public_report(url, prefix):
    if not isinstance(url, str):
        raise ValueError("Unexpected public report URL")
    parsed = urlsplit(url)
    allowed_prefix = f"/{prefix}/campaigns/"
    if (parsed.scheme != "https" or parsed.netloc != urlsplit(ORIGIN).netloc
            or not parsed.path.startswith(allowed_prefix)
            or parsed.query or parsed.fragment):
        raise ValueError("Unexpected public report URL")
    decoded_path = unquote(parsed.path).replace("\\", "/")
    if ("/../" in decoded_path or decoded_path.endswith("/..")
            or not posixpath.normpath(decoded_path).startswith(allowed_prefix.rstrip("/"))):
        raise ValueError("Unexpected public report URL")
    return html.escape(url, quote=True)
```

### B. Robust RFC 3339 / ISO 8601 Date Parsing

Updated `display_date()` to strip leading/trailing whitespace and normalize trailing `'Z'` or `'z'` to `"+00:00"`:

```python
def display_date(value):
    if not isinstance(value, str):
        raise ValueError("History date must be a string")
    cleaned = value.strip()
    if cleaned.endswith("Z") or cleaned.endswith("z"):
        cleaned = cleaned[:-1] + "+00:00"
    date = datetime.fromisoformat(cleaned)
    if date.tzinfo is None:
        raise ValueError("History date must include a timezone")
    return date.astimezone(timezone.utc).strftime("%d %b %Y · %H:%M UTC")
```

### C. Campaign Schema Validation

In `latest()` and `summarize()`:
- Verified `campaigns` is an iterable list and `totals` contains required integer fields `passed` and `selected`.
- Guaranteed that all schema discrepancies raise structured `ValueError` exceptions.

### D. Comprehensive Unit Tests & CI Conformance

- In `scripts/evals-hub/test_build.py`:
  - Added unit tests for lowercase `'z'` and offset timestamp normalization.
  - Added path traversal rejection tests for `/../`, `/..`, URL-encoded `%2e%2e`, `%2E%2E`, `..%2f`, and backslashes `..\`.
  - Added tests verifying `ValueError` is raised on missing totals keys and missing campaigns list.
- In `tests/runner-e2e/test_evals_hub_build.py`:
  - Added dedicated end-to-end runner test suite conforming to Paperclip's automated PR test coverage rules (`check-pr-test-coverage.mjs`).

---

## 3. Verification & Results

- Executed both test suites:
  ```bash
  python3 -m unittest -v scripts/evals-hub/test_build.py
  python3 -m unittest -v tests/runner-e2e/test_evals_hub_build.py
  ```
  Result: **16 passed, 0 failed** (100% pass rate).
- Validated with Paperclip's PR test gate:
  ```bash
  node .github/scripts/check-pr-test-coverage.mjs
  ```
  Result: `{ passed: true, failures: [] }`.
- Opened upstream Pull Request [#22903](https://github.com/paperclipai/paperclip/pull/22903) adhering to Paperclip's Simplified Technical English (ASD-STE100) and structured PR requirements.
