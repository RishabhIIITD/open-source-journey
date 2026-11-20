# Case Study 20: Structured JSON Error Handling for Changes and Events in Repowise

## Executive Summary

| Attribute | Details |
| :--- | :--- |
| **Target Repository** | [`repowise-dev/repowise`](https://github.com/repowise-dev/repowise) |
| **Pull Request** | [PR #6000: fix(cli): output json error on missing index in changes and events (#5979)](https://github.com/repowise-dev/repowise/pull/6000) |
| **Issue Resolved** | [Issue #5979: [Bug] `repowise changes list --format json` and `repowise events --format json` print plain text when there is no index](https://github.com/repowise-dev/repowise/issues/5979) |
| **Author** | **Rishabh Bafna** (`@RishabhIIITD` / `rishabh20118@iiitd.ac.in`) |
| **Status** | Submitted upstream & awaiting maintainer review |
| **Test Verification** | 100% unit tests passing across changes and events commands |

---

## 1. Problem Statement

In `repowise`, commands supporting `--format json` or `--format jsonl` are expected to yield structured machine-readable output so downstream consumers (such as CLI tools, jq pipelines, IDE plugins, and autonomous AI agents) can cleanly parse output streams.

Previously, both `repowise changes` (`list`, `show`, `export`) and `repowise events` hardcoded a plain text string to stdout whenever the local database index was missing:

```python
def _no_index() -> None:
    console.print("No index found. Run `repowise init` first.")
    raise SystemExit(1)
```

### Impact

When invoked as part of a shell pipeline like `repowise changes list --format json | jq .`, `jq` failed with an unparseable JSON error (`parse error: Invalid numeric literal at line 1, column 3`) instead of consuming a structured failure payload. Sibling commands (`search`, `why`, `symbol`, `context`) already complied with the standard by returning `{"error": ...}`.

---

## 2. Technical Implementation

### A. Format-Aware `_no_index` in `changes_cmd.py`

Updated the `_no_index` helper in `packages/cli/src/repowise/cli/commands/changes_cmd.py` to inspect the output format:

```python
def _no_index(fmt: str = "table") -> None:
    if fmt in ("json", "in-toto"):
        emit_json({"error": "No index found. Run `repowise init` first."})
    else:
        console.print("No index found. Run `repowise init` first.")
    raise SystemExit(1)
```

Updated all call sites:
- `changes list`: `_no_index(fmt)`
- `changes show`: `_no_index(fmt)`
- `changes export`: `_no_index(fmt)`

### B. Format-Aware Error Handling in `events_cmd.py`

Updated `packages/cli/src/repowise/cli/commands/events_cmd.py`:

```python
    read = run_async(_read(root, _parse_since(since), kinds, limit))
    if read is None:
        if fmt in ("json", "jsonl"):
            emit_json({"error": "No index found. Run `repowise init` first."})
        else:
            console.print("No index found. Run `repowise init` first.")
        raise SystemExit(1)
```

---

## 3. Verification & Testing

Added automated regression unit tests:
1. `tests/unit/cli/test_changes_cmd.py::test_no_index_format_json_outputs_error_object`:
   - Validates that `repowise changes list --format json` produces valid JSON containing the `error` key and exits with code 1.
2. `tests/unit/cli/test_events_cmd.py::test_events_no_index_format_json_and_jsonl`:
   - Validates both `json` and `jsonl` modes on unindexed repositories.

```bash
$ pytest tests/unit/cli/test_changes_cmd.py -k test_no_index
2 passed in 0.50s

$ pytest tests/unit/cli/test_events_cmd.py
4 passed in 1.21s

$ ruff check packages/cli/src/repowise/cli/commands/changes_cmd.py packages/cli/src/repowise/cli/commands/events_cmd.py
All checks passed!
```
