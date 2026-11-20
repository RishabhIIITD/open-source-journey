# 🚀 My Open Source Journey

Welcome to my open-source log! This repository documents my journey contributing to real-world, production open-source software. 

Rather than simply submitting code, each contribution is documented with a detailed technical case study covering:
- **Root-cause analysis & problem discovery**
- **Codebase investigation & dependency checks**
- **Community contribution guidelines & bot automation rules**
- **CI/CD pipelines, linters, and formatting fixes**
- **Key engineering takeaways**

---

## 📌 Contribution Log

| # | Project | Issue / PR | Tech Stack | Status | Deep Dive & Case Study |
|---|---|---|---|---|---|
| **01** | [**Internet Archive: Open Library**](https://github.com/internetarchive/openlibrary) | [PR #14536](https://github.com/internetarchive/openlibrary/pull/14536) <br> *(Issue #14534)* | Python, web.py, Solr | 🟢 Open / CI Passing | [📖 Case Study](./contributions/01-openlibrary-dead-endpoint/README.md) · [📄 PDF](./contributions/01-openlibrary-dead-endpoint/walkthrough-guide.pdf) |
| **02** | [**PyCalendar: icalendar**](https://github.com/PyCalendar/icalendar) | [PR #2144](https://github.com/PyCalendar/icalendar/pull/2144) <br> *(Issue #1797)* | Python, pytest, RFC 5545 | 🟢 Open / In Review | [📖 Case Study](./contributions/02-pycalendar-todo-completed/README.md) · [📄 PDF](./contributions/02-pycalendar-todo-completed/walkthrough-guide.pdf) |
| **03** | [**PyCalendar: icalendar**](https://github.com/PyCalendar/icalendar) | [PR #2168](https://github.com/PyCalendar/icalendar/pull/2168) <br> *(Issue #1851)* | Python, pytest, RFC 5545 | 🟢 Open / In Review | [📖 Case Study](./contributions/03-pycalendar-recur-byhour/README.md) · [📄 PDF](./contributions/03-pycalendar-recur-byhour/walkthrough-guide.pdf) |
| **04** | [**PyCalendar: icalendar**](https://github.com/PyCalendar/icalendar) | [PR #2169](https://github.com/PyCalendar/icalendar/pull/2169) <br> *(Issue #1851)* | Python, pytest, RFC 5545 | 🟢 Open / In Review | [📖 Case Study](./contributions/04-pycalendar-recur-byminute/README.md) · [📄 PDF](./contributions/04-pycalendar-recur-byminute/walkthrough-guide.pdf) |
| **05** | [**PyCalendar: icalendar**](https://github.com/PyCalendar/icalendar) | [PR #2170](https://github.com/PyCalendar/icalendar/pull/2170) <br> *(Issue #1851)* | Python, pytest, RFC 5545 | 🟢 Open / In Review | [📖 Case Study](./contributions/05-pycalendar-recur-bysecond/README.md) · [📄 PDF](./contributions/05-pycalendar-recur-bysecond/walkthrough-guide.pdf) |

---

## 🛠️ Key Takeaways & Practices
1. **Understand Before Modifying**: Use `git grep` and code inspection to confirm that deprecated functions/routes have zero remaining callers before proposing deletions.
2. **Respect Repository Automation**: Many production repositories (like Open Library) use bots to manage contributor triage; always check `CONTRIBUTING.md` before opening PRs.
3. **Automated CI Hygiene**: Use repository bot commands like `pre-commit.ci autofix` to keep code formatting compliant with project standards (PEP 8, Ruff).

---

## 👤 Author
- GitHub: [@RishabhIIITD](https://github.com/RishabhIIITD)
