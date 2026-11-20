# Case Study 19: Path Existence Validation for Repowise Watch Command

## Executive Summary

| Attribute | Details |
| :--- | :--- |
| **Target Repository** | [`repowise-dev/repowise`](https://github.com/repowise-dev/repowise) |
| **Pull Request** | [PR #5999: fix(cli): validate path existence in watch command (#5981)](https://github.com/repowise-dev/repowise/pull/5999) |
| **Issue Resolved** | [Issue #5981: [Bug] `repowise watch <missing path>` creates the directory and blocks forever](https://github.com/repowise-dev/repowise/issues/5981) |
| **Author** | **Rishabh Bafna** (`@RishabhIIITD` / `rishabh20118@iiitd.ac.in`) |
| **Status** | Submitted upstream & awaiting maintainer review |
| **Test Verification** | 29/29 unit tests passing (100%) |

---

## 1. Problem Statement

In `repowise`, the `watch` CLI command monitors a local repository for filesystem changes and automatically re-indexes changed files in the background.

Previously, the `path` argument was declared without any existence constraints:

```python
@click.command("watch")
@click.argument("path", required=False, default=None)
```

When a user invoked `repowise watch <missing_path>` (due to a typo or wrong working directory), execution entered `_watch_single_repo` which executed:

```python
ensure_repowise_dir(repo_path)
```

This unintentionally:
1. Created the non-existent folder on disk.
2. Created a `.repowise/` metadata subfolder inside it.
3. Started a filesystem watcher thread on this phantom folder and blocked indefinitely waiting for events that would never happen.

---

## 2. Technical Solution

Applied Click's built-in `click.Path(exists=True)` validator to the `path` argument, matching the established pattern in sibling commands such as `dead-code`:

```python
@click.command("watch")
@click.argument("path", required=False, default=None, type=click.Path(exists=True))
```

### Benefits
1. **Early Validation**: Click validates argument existence before any command logic or filesystem mutations can occur.
2. **Clear Usage Error**: If the path does not exist, Click immediately prints a descriptive usage error and exits with standard code `2`.
3. **No Unintended Side Effects**: Non-existent folders are never created on disk.
4. **Zero Regressions**: When `path` is omitted (defaults to `None` for current directory) or points to an existing directory, command behavior is 100% unchanged.

---

## 3. Verification & Testing

Added `test_watch_missing_path_exits_2` to `tests/unit/cli/test_watch_cmd.py`:

```python
def test_watch_missing_path_exits_2(tmp_path) -> None:
    """A missing path argument is rejected with exit code 2 and creates no directory (#5981)."""
    missing = tmp_path / "does_not_exist"
    result = CliRunner().invoke(cli, ["watch", str(missing)])

    assert result.exit_code == 2, result.output
    assert not missing.exists()
```

### Test Results

```bash
$ pytest tests/unit/cli/test_watch_cmd.py
======================= 29 passed in 0.97s =======================

$ ruff check packages/cli/src/repowise/cli/commands/watch_cmd.py tests/unit/cli/test_watch_cmd.py
All checks passed!
```
