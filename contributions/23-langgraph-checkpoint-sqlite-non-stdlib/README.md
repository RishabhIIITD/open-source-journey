# Case Study 23: LangGraph — Non-Stdlib Driver Compatibility in Checkpoint SQLite Saver

> **Target Repository**: [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph)  
> **Upstream PR**: [#9754](https://github.com/langchain-ai/langgraph/pull/9754)  
> **Linked Issue**: [#9561](https://github.com/langchain-ai/langgraph/issues/9561)  
> **Component**: `libs/checkpoint-sqlite/langgraph/checkpoint/sqlite` (`SqliteSaver` & `AsyncSqliteSaver`)  
> **Contributor**: Rishabh Bafna ([@RishabhIIITD](https://github.com/RishabhIIITD))  
> **Technologies**: Python 3.10+, SQLite, aiosqlite, sqlcipher3, apsw, Database Migrations, Pytest  

---

## 1. Executive Summary

In [LangGraph](https://github.com/langchain-ai/langgraph), persistence of state graphs and multi-agent execution threads is governed by checkpoint savers. For embedded local development and edge deployments, `SqliteSaver` and `AsyncSqliteSaver` provide checkpoint persistence using SQLite.

During graph execution setup, `SqliteSaver.setup()` and `AsyncSqliteSaver.setup()` run an inline migration step:
```sql
ALTER TABLE writes ADD COLUMN task_path TEXT NOT NULL DEFAULT ''
```
When initializing fresh databases, `CREATE TABLE writes` already includes `task_path`. SQLite throws an operational error (`duplicate column name: task_path`), which the setup logic catches and ignores.

However, the existing exception handlers only caught `sqlite3.OperationalError` (sync) and `aiosqlite.OperationalError` (async). When developers pass database connections from alternative or encrypted SQLite drivers (such as `sqlcipher3`, `apsw`, or custom DB-API proxies), these drivers raise their own `OperationalError` subclasses that do not inherit from Python's standard library `sqlite3.OperationalError`. As a result, the exception leaked unhandled, crashing database initialization on every fresh database.

This contribution broadens the migration exception guard to catch driver-specific `OperationalError` exceptions, normalizes error message inspection across drivers, and adds a regression test suite covering both synchronous and asynchronous drivers.

---

## 2. Root Cause & Architectural Analysis

### The Flawed Exception Catch
In `libs/checkpoint-sqlite/langgraph/checkpoint/sqlite/__init__.py`:
```python
# Before PR #9754
try:
    self.conn.execute(
        "ALTER TABLE writes ADD COLUMN task_path TEXT NOT NULL DEFAULT ''"
    )
except sqlite3.OperationalError as e:
    if "readonly database" in str(e):
        self._has_task_path = False
    elif "duplicate column name" not in str(e):
        raise
```

And in `libs/checkpoint-sqlite/langgraph/checkpoint/sqlite/aio.py`:
```python
# Before PR #9754
try:
    await self.conn.execute(
        "ALTER TABLE writes ADD COLUMN task_path TEXT NOT NULL DEFAULT ''"
    )
    await self.conn.commit()
except aiosqlite.OperationalError as e:
    if "readonly database" in str(e):
        self._has_task_path = False
    elif "duplicate column name" not in str(e):
        raise
```

### The Driver Exception Hierarchy Problem
Python's PEP 249 specifies DB-API 2.0 error hierarchies (`DatabaseError -> OperationalError`). However, independent C-extension drivers like `sqlcipher3` or `apsw` construct their own `OperationalError` exception types under their own module namespace.

```text
Standard Library:   sqlite3.OperationalError ──> sqlite3.DatabaseError ──> sqlite3.Error ──> Exception
Non-Stdlib Driver: sqlcipher3.OperationalError ──> sqlcipher3.DatabaseError ──> ... ──> Exception
```

Because `sqlcipher3.OperationalError` is **not** a subclass of `sqlite3.OperationalError`:
1. `except sqlite3.OperationalError:` does not match.
2. The exception bypasses the guard entirely.
3. Every encrypted SQLite database initialization crashes on startup with `duplicate column name: task_path`.

---

## 3. The Solution

We broadened the exception handling in both `SqliteSaver.setup()` and `AsyncSqliteSaver.setup()`:
1. Catch `(sqlite3.OperationalError, Exception)` and `(aiosqlite.OperationalError, Exception)`.
2. Inspect `str(e).lower()` case-insensitively for `"readonly database"` and `"duplicate column name"`.
3. If neither substring is present, re-raise the exception immediately to preserve safety for unexpected SQL syntax or filesystem errors.

```python
# libs/checkpoint-sqlite/langgraph/checkpoint/sqlite/__init__.py
try:
    self.conn.execute(
        "ALTER TABLE writes ADD COLUMN task_path TEXT NOT NULL DEFAULT ''"
    )
except (sqlite3.OperationalError, Exception) as e:
    error_msg = str(e).lower()
    if "readonly database" in error_msg:
        self._has_task_path = False
    elif "duplicate column name" not in error_msg:
        raise
```

```python
# libs/checkpoint-sqlite/langgraph/checkpoint/sqlite/aio.py
try:
    await self.conn.execute(
        "ALTER TABLE writes ADD COLUMN task_path TEXT NOT NULL DEFAULT ''"
    )
    await self.conn.commit()
except (aiosqlite.OperationalError, Exception) as e:
    error_msg = str(e).lower()
    if "readonly database" in error_msg:
        self._has_task_path = False
    elif "duplicate column name" not in error_msg:
        raise
```

---

## 4. Verification & Testing

Added unit tests to `libs/checkpoint-sqlite/tests/test_writes_task_path_migration.py`:
- `test_setup_handles_non_stdlib_driver_duplicate_column_error`: Tests synchronous `SqliteSaver` using a connection proxy simulating driver-isolated `CustomDriverOperationalError("duplicate column name: task_path")`.
- `test_async_setup_handles_non_stdlib_driver_duplicate_column_error`: Tests asynchronous `AsyncSqliteSaver` using an async connection wrapper raising `CustomDriverOperationalError`.
- Verified 10/10 migration tests pass in 0.09s.
- Verified all 178 tests across `libs/checkpoint-sqlite` pass cleanly without regressions.
- Code validated with `ruff check .` and `ruff format --check .`.
