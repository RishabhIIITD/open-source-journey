# Contribution 02: PyCalendar / icalendar
## Adding `COMPLETED` Property to `Todo` (RFC 5545 Section 3.8.2.1)

- **Repository**: [PyCalendar/icalendar](https://github.com/PyCalendar/icalendar)
- **Pull Request**: [#2144](https://github.com/PyCalendar/icalendar/pull/2144)
- **Linked Issue**: [#1797](https://github.com/PyCalendar/icalendar/issues/1797)
- **Tech Stack**: Python 3, `pytest`, `ruff`, RFC 5545 Calendar Standards

---

## 1. Problem Statement
The `icalendar` Python library is the standard Python package for parsing and generating RFC 5545 iCalendar files. While components like `Event` and `Component` had `DTSTAMP`, `CREATED`, and `LAST_MODIFIED` accessors returning timezone-aware UTC timestamps, `Todo` (representing a `VTODO` task) was missing a dedicated accessor for `COMPLETED`.

Accessing `todo.COMPLETED` resulted in:
```python
AttributeError: 'Todo' object has no attribute 'COMPLETED'
```

---

## 2. Technical Investigation & RFC Conformance
* **RFC 5545 Section 3.8.2.1**: Specifies `COMPLETED` as defining the date and time that a to-do was actually completed.
* **Component Conformance**: Verified that `COMPLETED` is valid *only* on `VTODO` calendar components (not `VEVENT`, `VJOURNAL`, or `VTIMEZONE`).
* **Format & Timezones**: RFC 5545 states that the date-time value MUST be in UTC format. If input as a `DATE` (e.g. `COMPLETED;VALUE=DATE:20070501` or `COMPLETED:20070501`), the library normalizes it into a UTC `datetime` at `00:00:00+00:00`.

---

## 3. Implementation Details
1. **Property Accessor**:
   Added `COMPLETED = single_utc_property("COMPLETED", ...)` in `src/icalendar/cal/todo.py`.
2. **Lowercase Accessor & Setters**:
   Added `completed` property getter, setter, and deleter to follow the library's design patterns:
   ```python
   @property
   def completed(self) -> datetime | None:
       return self.COMPLETED

   @completed.setter
   def completed(self, completed: date | datetime | None):
       self.COMPLETED = completed

   @completed.deleter
   def completed(self):
       del self.COMPLETED
   ```
3. **Constructor Support**:
   Updated `Todo.new(...)` to accept `completed: date | datetime | None = None` and initialize `todo.completed = completed`.
4. **Test Suite & Fixtures**:
   - Added fixture files `issue_1797_completed_date.ics` and `issue_1797_completed_datetime.ics` in `src/icalendar/tests/todos/`.
   - Created `src/icalendar/tests/test_issue_1797_todo_completed.py` testing both RFC date conversions, fixture loading, setters, deleters, and non-presence on other components. All 9 tests passed.
5. **Towncrier News Entry**:
   Created `news/+1797-todo-completed.feature` for automatic changelog release generation.

---

## 4. Key Takeaways
- Building on established core abstractions (like `single_utc_property`) ensures that serialization, timezone localization, and error handling are uniformly enforced.
- Providing both uppercase RFC attributes (`todo.COMPLETED`) and idiomatic Python lowercase attributes (`todo.completed`) makes open-source libraries comfortable for developers with different background styles.
