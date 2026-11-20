# 📘 Open Source Contributor Playbook

A structured, beginner-friendly engineering guide for navigating, contributing to, and landing pull requests in production open-source codebases.

---

## 1. Finding & Evaluating Issues

### Where to Look
- **Labels**: Look for `good first issue`, `help wanted`, `documentation`, or `bug` on target repositories.
- **RFC Implementations**: Standard compliance tasks (e.g. RFC 5545 recurrence rules, API route standards) are great entry points because the expected behavior is rigorously documented in specifications.

### Sanity Checks Before Coding:
1. Is someone already assigned or has an open pull request addressed it?
2. Is the issue clear and reproducible?
3. What is the maintainers' activity cadence (recent merges in the last 30 days)?

---

## 2. Forking & Branch Hygiene

```bash
# 1. Fork on GitHub and clone your fork
git clone https://github.com/<your-username>/<repo>.git
cd <repo>

# 2. Add upstream remote to stay synced
git remote add upstream https://github.com/<upstream-org>/<repo>.git
git fetch upstream

# 3. Create a focused topic branch from upstream main
git checkout -b fix/clear-descriptive-slug upstream/main
```

---

## 3. Atomic Commits & Co-Authorship

- Keep each commit focused on one logical change.
- Follow the **Conventional Commits** specification:
  - `fix:` for bug fixes
  - `feat:` for new capabilities
  - `docs:` for documentation updates
  - `test:` for adding or improving test suites
  - `refactor:` for code restructurings

### Co-Authorship Syntax
To credit multiple contributors, leave a blank line and append:
```text
Co-authored-by: Name <verified-email@example.com>
```

---

## 4. Pull Request Excellence

1. **Title**: Follow conventional commit conventions (`fix(cli): resolve uncaught exception in ...`).
2. **Context**: Explain *why* the change is necessary, not just *what* code changed.
3. **Reference Issue**: Use GitHub keywords to auto-link and close issues:
   - `Fixes #1234` or `Resolves #5678`
4. **Test Evidence**: Include test output logs, screenshots, or before/after execution examples.

---

## 5. Navigating Code Reviews

- Welcome constructive feedback with humility and technical precision.
- Push clean follow-up commits or interactive rebases as requested by maintainers.
- Never force push over shared review branches without maintainer coordination.
