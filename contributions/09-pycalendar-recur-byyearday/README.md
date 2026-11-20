# 📖 Case Study 09: Implementing RFC 5545 BYYEARDAY Property Accessor for vRecur in PyCalendar / icalendar

**Repository:** [PyCalendar/icalendar](https://github.com/PyCalendar/icalendar)  
**Issue:** [#1851 - property accessors for vRecur (first-timer collaboration)](https://github.com/PyCalendar/icalendar/issues/1851)  
**Pull Request:** [PR #2174 - feat(recur): add byyearday property accessor to vRecur (#1851)](https://github.com/PyCalendar/icalendar/pull/2174)  
**Author:** [@RishabhIIITD](https://github.com/RishabhIIITD) (Rishabh Bafna)  
**Tech Stack:** Python 3, RFC 5545 Recurrence Specification, pytest, Towncrier, GitHub Actions  
**PR Status:** 🟢 Open / CI Checks Running  
**Documentation:** [📄 Download Formatted PDF Guide](./walkthrough-guide.pdf)

---

## 🎯 1. Executive Summary

This case study documents an open-source feature contribution to **PyCalendar / icalendar**, implementing the `byyearday` property accessor on the `vRecur` recurrence dictionary in strict accordance with **RFC 5545 Section 3.3.10**.

The property provides typed getter, setter, and deleter accessors to the `BYYEARDAY` part of recurrence rules, enforcing day-of-year range constraints ([-366..-1] and [1..366], with 0 strictly prohibited), handling scalar and iterable assignment, and delivering 100% test coverage with 26 unit tests.

```mermaid
flowchart TD
    RFC["RFC 5545 Recurrence Rule (Section 3.3.10)"] --> Grammar["BYYEARDAY = -366..-1 or 1..366 (0 Forbidden)"]
    Grammar --> Recur["vRecur (Recurrence Dictionary)"]
    
    Recur --> Getter["recur.byyearday -> tuple[int, ...]"]
    Recur --> Setter["recur.byyearday = [1, 100, 300] -> stores vInt instances"]
    Recur --> Deleter["del recur.byyearday / recur.byyearday = None -> removes part"]
    
    Getter --> Val["Validates Range (-366..-1, 1..366); InvalidCalendar on 0 or out-of-range"]
    Setter --> ValType["Validates int type; TypeError on non-int"]
```

---

## 🔍 2. The Problem Statement & Requirements

### The Collaborative Initiative (Issue #1851)
RFC 5545 recurrence rules (`RRULE`) allow yearly recurrence schedules to target specific days of the year (such as the 100th day or the last day of the year) via `BYYEARDAY`.

### RFC 5545 Specification
From **RFC 5545 Section 3.3.10**:
> *"The BYYEARDAY rule part specifies a COMMA-separated list of days of the year. Valid values are 1 to 366 or -366 to -1. For example, -1 represents the last day of the year (December 31st) and -306 represents the 306th to the last day of the year (March 1st)."*
> *"Each BYYEARDAY value MUST be between 1 and 366 or between -366 and -1."*
> *"The value 0 MUST NOT be used."*

### Implementation Checklist
- [x] Return type is `tuple[int, ...]` based on `vRecur.types`.
- [x] Setting to `None` or an empty sequence deletes the value.
- [x] `del recur.byyearday` deletes the value.
- [x] If multiple values are given, they all are returned.
- [x] If an empty list or missing, `()` is returned.
- [x] Validates positive ranges [1..366] and negative ranges [-366..-1].
- [x] The value `0` explicitly raises `InvalidCalendar`.
- [x] Non-integer values raise `TypeError`.
- [x] Docstrings with doctest examples and range documentation.

---

## 💻 3. Implementation Details

In `src/icalendar/prop/recur/recur.py`, we implemented `byyearday`:

```python
    @property
    def byyearday(self) -> tuple[int, ...]:
        """The BYYEARDAY part of the recurrence rule.

        This specifies a list of days of the year for the recurrence, per
        :rfc:`5545#section-3.3.10`. Valid values are integers from 1 to 366
        or from -366 to -1. The value 0 is not allowed.

        Returns:
            A tuple of integer days of the year, or an empty tuple if ``BYYEARDAY`` is not set.

        Raises:
            InvalidCalendar: if a stored value cannot be converted to int, is 0,
                or is outside the valid ranges of -366 to -1 or 1 to 366.

        Example:
            ..  code-block:: pycon

                >>> from icalendar.prop import vRecur
                >>> vRecur.from_ical("FREQ=YEARLY;BYYEARDAY=1,100,300").byyearday
                (1, 100, 300)
                >>> vRecur.from_ical("FREQ=YEARLY;BYYEARDAY=-1").byyearday
                (-1,)
                >>> vRecur.from_ical("FREQ=YEARLY").byyearday
                ()
        """
        values = self.get("BYYEARDAY")
        if values is None:
            return ()
        if not isinstance(values, SEQUENCE_TYPES):
            values = [values]
        result: list[int] = []
        for val in values:
            if isinstance(val, bool):
                raise InvalidCalendar(f"BYYEARDAY values must be integers, got {val!r}")
            try:
                day = int(val)
            except (TypeError, ValueError) as e:
                raise InvalidCalendar(
                    f"BYYEARDAY values must be integers, got {val!r}"
                ) from e
            if day == 0 or not -366 <= day <= 366:
                raise InvalidCalendar(
                    "BYYEARDAY values must be between -366 and -1 or 1 and 366, "
                    f"got {day}"
                )
            result.append(day)
        return tuple(result)

    @byyearday.setter
    def byyearday(self, value: int | Iterable[int] | None) -> None:
        """Set the BYYEARDAY part of the recurrence rule, or delete it if None or empty."""
        if value is None:
            del self.byyearday
            return
        if isinstance(value, int) and not isinstance(value, bool):
            days = [value]
        elif isinstance(value, Iterable) and not isinstance(value, (str, bytes)):
            days = list(value)
        else:
            raise TypeError(
                f"byyearday must be an int or an iterable of ints, got {value!r}"
            )
        if not days:
            del self.byyearday
            return
        validated: list[vInt] = []
        for d in days:
            if not isinstance(d, int) or isinstance(d, bool):
                raise TypeError(f"byyearday items must be integers, got {d!r}")
            if d == 0 or not -366 <= d <= 366:
                raise InvalidCalendar(
                    "BYYEARDAY values must be between -366 and -1 or 1 and 366, "
                    f"got {d}"
                )
            validated.append(vInt(d))
        self["BYYEARDAY"] = validated

    @byyearday.deleter
    def byyearday(self) -> None:
        """Delete the BYYEARDAY part of the recurrence rule."""
        self.pop("BYYEARDAY", None)
```

---

## 🧪 4. Testing & Verification

We created `src/icalendar/tests/prop/recur/test_byyearday.py` with 26 unit tests covering:
- Boundary conditions (-366, -1, 1, 366).
- Prohibition of 0 per RFC 5545 Section 3.3.10.
- Rejection of out-of-range days (e.g. -367, 367, 500).
- Roundtrip preservation through `.to_ical()`.

```bash
PYTHONPATH=src pytest src/icalendar/tests/prop/recur/test_byyearday.py
# 26 passed in 0.04s
```

---

## 📰 5. Towncrier Changelog Fragment

Created `news/1851.feature.8`:
```text
Added a ``byyearday`` property accessor to :class:`~icalendar.prop.recur.recur.vRecur` for getting, setting, and deleting the ``BYYEARDAY`` part of a recurrence rule. @RishabhIIITD
```

---

## 🏆 6. Summary of Changes

| Metric | Detail |
|---|---|
| **Pull Request** | [PyCalendar/icalendar#2174](https://github.com/PyCalendar/icalendar/pull/2174) |
| **Branch** | `RishabhIIITD:feat/recur-byyearday-property` |
| **Files Modified** | 1 (`src/icalendar/prop/recur/recur.py`) |
| **Files Created** | 2 (`news/1851.feature.8`, `src/icalendar/tests/prop/recur/test_byyearday.py`) |
| **Net Changes** | +240 lines, 0 deletions |
| **Test Result** | 100% Passing (26 tests) |
