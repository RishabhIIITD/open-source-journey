# Case Study 22: CrewAI — Monotonic Versioning and Extension Isolation in LocalArtifactStore

> **Target Repository**: [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)  
> **Upstream PR**: [#9600](https://github.com/crewAIInc/crewAI/pull/9600)  
> **Linked Issue**: [#9599](https://github.com/crewAIInc/crewAI/issues/9599)  
> **Component**: `lib/crewai/src/crewai/artifacts.py` (`LocalArtifactStore`)  
> **Contributor**: Rishabh Bafna ([@RishabhIIITD](https://github.com/RishabhIIITD))  
> **Technologies**: Python 3.12+, Pydantic v2, File Systems, Monotonic Versioning, Pytest  

---

## 1. Executive Summary

In `crewAI`, the newly released **Artifacts** subsystem enables autonomous agents to generate, persist, and version structured deliverables (such as Markdown documents, SVG diagrams, PDF summaries, and CSV datasets) within an execution run.

The storage engine (`LocalArtifactStore`) previously determined the next version number by counting existing entries via `len(list(directory.glob("v*.*"))) + 1`. This introduced a critical race condition and state corruption bug: whenever earlier versions were pruned/cleaned up, or when an agent saved deliverables of different media types under the same identifier, the version counter would collide with existing versions on disk. Furthermore, because atomic writes checked for collision against `f"v{version}.{extension}"`, a new `.png` file would not collide with an existing `.svg` file on the filesystem. Consequently, multiple distinct files coexisted under the same version number (e.g. both `v2.svg` and `v2.png`), leading `load()` to overwrite one version in its dictionary and lose access to the artifact.

This contribution implements strictly monotonic versioning using integer parsing `max(existing_versions, default=0) + 1` and cross-extension isolation checks before writing, backed by a comprehensive regression test suite.

---

## 2. Root Cause & Architectural Flaw

### The Faulty Implementation
```python
# lib/crewai/src/crewai/artifacts.py (prior to PR #9600)
directory = self.root / execution_id / artifact.identifier
directory.mkdir(parents=True, exist_ok=True)
version = len(list(directory.glob("v*.*"))) + 1
while True:
    path = directory / f"v{version}.{extension}"
    try:
        with path.open("xb") as file:
            file.write(data)
        break
    except FileExistsError:
        version += 1
```

### The Three Failure Modes
1. **Pruned / Deleted Versions**: If an artifact directory held `v1.html` and `v2.svg`, and `v1.html` was pruned by retention policies, `len(directory.glob("v*.*"))` became `1`. The next save evaluated `1 + 1 = 2`.
2. **Cross-Extension Collision**: Because `open("xb")` was checked only for `f"v2.{extension}"`, saving a `.png` file found no `v2.png` and succeeded, coexisting with `v2.svg`.
3. **Lookup Overwrite in `load()`**:
   ```python
   versions = {
       int(path.stem[1:]): path
       for path in directory.glob("v*.*")
       if path.stem[1:].isdigit()
   }
   ```
   Both `v2.svg` and `v2.png` keyed on `2`. The dictionary comprehension arbitrarily stored only one of them, rendering the other permanently inaccessible.

---

## 3. The Solution

We refactored `LocalArtifactStore.save` to ensure mathematical monotonicity and cross-extension uniqueness:

```python
# lib/crewai/src/crewai/artifacts.py (PR #9600)
directory = self.root / execution_id / artifact.identifier
directory.mkdir(parents=True, exist_ok=True)
existing_versions = [
    int(path.stem[1:])
    for path in directory.glob("v*.*")
    if path.is_file() and path.stem[1:].isdigit()
]
version = max(existing_versions, default=0) + 1
while True:
    while any(directory.glob(f"v{version}.*")):
        version += 1
    path = directory / f"v{version}.{extension}"
    try:
        with path.open("xb") as file:
            file.write(data)
        break
    except FileExistsError:
        version += 1
```

---

## 4. Verification & Testing

Added `test_local_store_version_isolation_with_pruned_versions_and_extension_changes` to `lib/crewai/tests/test_artifacts.py`:
- Populates `v1.html` and `v2.svg`.
- Deletes `v1.html`.
- Saves a new artifact with kind `image` (`.png`).
- Asserts that the new artifact receives version `3` (not `2`).
- Verifies that `v2.svg` and `v3.png` both persist and load correctly.
- Verified all 76 tests in `test_artifacts.py` pass cleanly (100% pass rate).
