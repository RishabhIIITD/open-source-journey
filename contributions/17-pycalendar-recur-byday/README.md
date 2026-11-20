# Case Study 17: Implement `byday` and `byweekday` Property Accessors on `vRecur` in PyCalendar

## Executive Summary

| Attribute | Details |
| :--- | :--- |
| **Target Repository** | [`PyCalendar/icalendar`](https://github.com/PyCalendar/icalendar) |
| **Pull Request** | [PR #2182: feat(recur): add byday and byweekday property accessors (#1851)](https://github.com/PyCalendar/icalendar/pull/2182) |
| **Issue Resolved** | [Issue #1851: property accessors for vRecur (first-timer collaboration)](https://github.com/PyCalendar/icalendar/issues/1851) |
| **Standards & Specs** | RFC 5545 §3.3.10 (Recurrence Rule) & §3.8.5.3 |
| **Author** | **Rishabh Bafna** (`@RishabhIIITD` / `rishabh20118@iiitd.ac.in`) |
| **Status** | Submitted upstream & awaiting maintainer review |
| **Test Verification** | 18/18 unit tests passing (100%), full recur suite (55/55 passing) |

---

## 1. Context & Specification

In iCalendar (:rfc:`5545#section-3.3.10`), the `RRULE` property uses `BYDAY` to specify days of the week on which events recur. Each day abbreviation (`MO`, `TU`, `WE`, `TH`, `FR`, `SA`, `SU`) may also be preceded by a positive (`+n`) or negative (`-n`) integer to indicate the nth occurrence within a monthly or yearly recurrence rule (e.g., `+1MO` for first Monday, `-2FR` for second-to-last Friday).

Historically, `vRecur` acted primarily as a `CaselessDict` subclass where recurrence rule parts were accessed via dictionary keys (`recur["BYDAY"]`), requiring manual type parsing and casting. Issue #1851 created a collaborative roadmap to add first-class Python property accessors (`getter`, `setter`, `deleter`) to `vRecur`.

Furthermore, Python's `dateutil` uses the spelling `byweekday`. Issue #1854 and #1851 specified that `byweekday` must be supported as a complete alias for `byday`.

---

## 2. Technical Implementation

In `src/icalendar/prop/recur/recur.py`:

### A. The `byday` Property

1. **Getter (`@property def byday(self) -> tuple[vWeekday, ...]:`)**:
   - Returns an empty tuple `()` when `BYDAY` is omitted or empty.
   - Normalizes single items or sequences into a tuple of `vWeekday` instances.
   - Raises `InvalidCalendar` if stored values cannot be parsed into valid weekdays.

2. **Setter (`@byday.setter`)**:
   - Deletes the property when assigned `None` or an empty iterable (`[]`, `()`).
   - Accepts a single string (`"MO"`), a single `vWeekday`, or an iterable of strings/`vWeekday` instances.
   - Validates each element against `vWeekday.from_ical()`, raising `InvalidCalendar` on invalid weekday strings and `TypeError` on invalid types.

3. **Deleter (`@byday.deleter`)**:
   - Cleans up both `BYDAY` and `BYWEEKDAY` keys from the underlying dictionary.

### B. The `byweekday` Alias

Exposed `@property def byweekday` with matching getter, setter, and deleter delegating cleanly to `byday`.

---

## 3. Verification & Testing

Created `src/icalendar/tests/prop/recur/test_byday.py` containing 18 unit tests:
- Absent key handling returning `()`
- Empty list handling returning `()`
- Single and multiple weekday parsing
- Positional weekday parsing (`+1MO`, `-2FR`)
- `byweekday` alias parity (getter, setter, deleter)
- Type validation and `TypeError` / `InvalidCalendar` error checks
- `to_ical()` serialization roundtrips

```bash
$ pytest src/icalendar/tests/prop/recur/test_byday.py
============================== 18 passed in 0.03s ==============================

$ pytest src/icalendar/tests/prop/recur/
============================== 55 passed in 0.04s ==============================

$ ruff check src/icalendar/prop/recur/recur.py src/icalendar/tests/prop/recur/test_byday.py
All checks passed!
```
