# Case Study 18: Standardize Failure Exit Codes in Repowise CLI Delete Command

## Executive Summary

| Attribute | Details |
| :--- | :--- |
| **Target Repository** | [`repowise-dev/repowise`](https://github.com/repowise-dev/repowise) |
| **Pull Request** | [PR #5996: fix(cli): exit 1 on delete command failure branches (#5980)](https://github.com/repowise-dev/repowise/pull/5996) |
| **Issue Resolved** | [Issue #5980: [Bug] `repowise delete <unknown id>` prints "not found" and exits 0](https://github.com/repowise-dev/repowise/issues/5980) |
| **Author** | **Rishabh Bafna** (`@RishabhIIITD` / `rishabh20118@iiitd.ac.in`) |
| **Status** | 🟣 Merged upstream into `main` by `@RaghavChamadiya` on Nov 21, 2026 |
| **Test Verification** | 4/4 unit tests passing (100%), 5/5 integration tests passing (100%) |

---

## 1. Problem Statement

[Repowise](https://github.com/repowise-dev/repowise) is an open-source codebase knowledge graph and architecture documentation engine.

In `packages/cli/src/repowise/cli/commands/delete_cmd.py`, several error paths reported a missing or unmatched repository and terminated with a bare `return`:

```python
if target is None:
    console.print(f"[red]Repository {target_id} not found.[/red]")
    await engine.dispose()
    return
```

The same silent success behavior occurred when:
1. `wiki.db` was not found (`Database not found.`)
2. No repository matched the specified `--path` (`No repository in the database matches...`)
3. The interactive selection was invalid (`Invalid selection.`)

### Impact

Because the command returned normally instead of raising an exit exception, the process terminated with exit status `0`. Shell scripts, CI/CD pipelines, and automated cleanup agents checking `$?` had no way to distinguish a successful deletion from a failure or no-op.

---

## 2. Technical Solution

### A. Failure Branch Refactoring

Updated all four failure branches in `packages/cli/src/repowise/cli/commands/delete_cmd.py` to raise `SystemExit(1)` (or `raise SystemExit(1) from None` within exception handlers) while preserving asynchronous resource cleanup (`await engine.dispose()`):

1. **Missing Database**:
   ```python
   if not db_path.exists():
       console.print("[yellow]Database not found.[/yellow]")
       raise SystemExit(1)
   ```

2. **Unmatched `--path`**:
   ```python
   if match is None:
       console.print(f"[yellow]No repository in the database matches {repo_path}.[/yellow]")
       await engine.dispose()
       raise SystemExit(1)
   ```

3. **Invalid Interactive Selection**:
   ```python
   except (ValueError, IndexError):
       console.print("[red]Invalid selection.[/red]")
       await engine.dispose()
       raise SystemExit(1) from None
   ```

4. **Unknown Repository ID**:
   ```python
   if target is None:
       console.print(f"[red]Repository {target_id} not found.[/red]")
       await engine.dispose()
       raise SystemExit(1)
   ```

### B. User Experience Invariance

User-initiated cancellations (e.g. typing `'q'` to quit the interactive selection or declining the confirmation prompt) remain normal exits (`0`).

---

## 3. Verification & Testing

1. Created dedicated unit test suite `tests/unit/cli/test_delete_cmd.py`:
   - `test_delete_missing_database_exits_1`
   - `test_delete_unknown_id_exits_1`
   - `test_delete_unmatched_path_exits_1`
   - `test_delete_invalid_selection_exits_1`
2. Updated integration tests in `tests/integration/test_cli.py::TestDeleteWithConfiguredDb`.
3. Ran full test suite:
   ```bash
   $ pytest tests/unit/cli/test_delete_cmd.py
   4 passed in 1.00s

   $ pytest tests/integration/test_cli.py -k TestDeleteWithConfiguredDb
   5 passed in 0.96s
   ```
