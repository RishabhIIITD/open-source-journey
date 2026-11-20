# 📖 RFC Reference Dictionary & Cross-Protocol Index

A technical glossary covering key specifications and engineering protocols implemented throughout the **open-source-journey** contributions.

---

## 1. RFC 5545: Internet Calendaring and Scheduling (iCalendar)

RFC 5545 defines the MIME message format for calendaring and scheduling exchange across email, web cal, and event synchronization servers.

### Core Components
| Component | Description |
| :--- | :--- |
| `VEVENT` | A scheduled appointment, meeting, or milestone with a start and end/duration. |
| `VTODO` | An action-item or assignment with status attributes (`COMPLETED`, `IN-PROCESS`). |
| `VJOURNAL` | A text-based journal or meeting notes record. |
| `VTIMEZONE` | Time zone definitions specifying UTC offsets and daylight saving transitions. |

### Recurrence Rules (`RRULE` / `vRecur`)
The recurrence rule defines algorithmic repetition for recurring events:
- **`FREQ`**: Recurrence frequency (`SECONDLY`, `MINUTELY`, `HOURLY`, `DAILY`, `WEEKLY`, `MONTHLY`, `YEARLY`).
- **`INTERVAL`**: Step size (e.g., `FREQ=WEEKLY;INTERVAL=2` represents bi-weekly).
- **`BYSECOND` / `BYMINUTE` / `BYHOUR`**: Expands or filters occurrences to specific seconds, minutes, or hours.
- **`BYDAY`**: Constrains occurrences to specific days of the week (`MO`, `TU`, `WE`, `TH`, `FR`, `SA`, `SU`). Supports ordinal prefixes (e.g. `1MO` for first Monday, `-1FR` for last Friday).
- **`BYMONTHDAY`**: Specifies days of the month (`1` to `31`, or negative offsets like `-1` for the last day).
- **`BYYEARDAY`**: Specifies day numbers within the year (`1` to `366`, `-366` to `-1`).
- **`BYWEEKNO`**: Specifies ISO 8601 week numbers (`1` to `53`).
- **`BYSETPOS`**: Filters results from other `BYxxx` rules to a specific set position (e.g. `BYDAY=MO,TU,WE;BYSETPOS=1`).
- **`WKST`**: Week start day definition (defaults to `MO`).
- **`RSCALE` (RFC 7529)**: Extension supporting non-Gregorian calendar scales (Hebrew, Islamic, Chinese, Ethiopic).
- **`SKIP` (RFC 7529)**: Handling for leap months and non-existent calendar dates (`OMIT`, `BACKWARD`, `FORWARD`).

---

## 2. Distributed Telemetry & Database Protocols

### SQLite WAL Mode (Write-Ahead Logging)
- **Mechanics**: Instead of writing changes directly to the database file, changes are appended to a separate `-wal` file.
- **Concurrent Readers/Writers**: Readers never block writers, and writers never block readers, delivering dramatic concurrency improvements in local agent telemetry.
- **`PRAGMA synchronous = NORMAL`**: Balances durability and throughput by syncing to disk at WAL checkpoints rather than on every transaction.
- **`PRAGMA busy_timeout`**: Automatically retries locks under contention instead of throwing immediate `database is locked` errors.
