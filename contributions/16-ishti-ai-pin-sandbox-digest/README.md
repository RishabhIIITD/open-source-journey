# Case Study 16: Pin Sandbox Docker Image by Digest in Ishti AI

## Executive Summary

| Attribute | Details |
| :--- | :--- |
| **Target Repository** | [`ishtiaq-ahmed-dev/ishti-ai`](https://github.com/ishtiaq-ahmed-dev/ishti-ai) |
| **Pull Request** | [PR #12: fix(sandbox): pin python:3.12-slim image by multi-arch digest (#5)](https://github.com/ishtiaq-ahmed-dev/ishti-ai/pull/12) |
| **Issue Resolved** | [Issue #5: Pin the sandbox image by digest](https://github.com/ishtiaq-ahmed-dev/ishti-ai/issues/5) |
| **Author** | **Rishabh Bafna** (`@RishabhIIITD` / `rishabh20118@iiitd.ac.in`) |
| **Status** | Submitted upstream & awaiting maintainer review |
| **Test Verification** | 12/12 unit tests passing (100%) |

---

## 1. Context & Motivation

[Ishti AI](https://github.com/ishtiaq-ahmed-dev/ishti-ai) is an open-source, voice-enabled personal AI assistant featuring local memory and hardened containerized execution skills. To execute user-submitted Python scripts or model scratchpad code without risking host machine compromise, Ishti provides a throwaway Docker sandbox skill (`ishti/skills/sandbox/skill.py`).

The container runs with strict isolation flags:
- `--network none`
- `--read-only` root filesystem
- `--cap-drop ALL`
- `--security-opt no-new-privileges`
- `--pids-limit 64`
- `--memory 256m`
- Unprivileged user (`65534:65534`)
- Ephemeral writable `tmpfs` at `/tmp`

### The Problem

Previously, `skill.py` launched the sandbox container using a floating tag:
```python
IMAGE = "python:3.12-slim"
```
While convenient during initial development, floating image tags introduce significant supply-chain risks and reproducibility issues:
1. **Supply-Chain Drift**: Upstream tag updates can inadvertently introduce breaking changes, modified runtime defaults, or vulnerabilities without warning.
2. **Inconsistent Environments**: Two different users pulling `python:3.12-slim` at different times could end up running differing container layers.
3. **Architectural Divergence**: Without explicit digest pinning, there is no cryptographic guarantee of image integrity.

In contrast, Ishti's WhatsApp bridge (`ishti/wa_bridge.py`) already adhered to the best practice of pinning WAHA by its cryptographic SHA-256 digest.

---

## 2. Technical Solution

### A. Pinning to Multi-Architecture Digest

To preserve cross-platform support across both `x86_64` (`amd64`) and Apple Silicon / ARM64 (`arm64`), the multi-architecture manifest list digest from the official Docker Hub Python registry was selected:
```
python:3.12-slim@sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b
```

### B. Code Implementation

In `ishti/skills/sandbox/skill.py`:
```python
# pinned by multi-arch digest; a floating tag could change underneath users.
# To bump: run `docker buildx imagetools inspect python:3.12-slim` or query Docker Hub for the manifest list digest.
DEFAULT_IMAGE = "python:3.12-slim@sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b"
IMAGE = os.environ.get("ISHTI_SANDBOX_IMAGE") or DEFAULT_IMAGE
```

Key features:
1. **Immutable Default**: Defaults to the verified, cryptographically pinned multi-arch digest.
2. **Configurable Override**: Allows power users or enterprise deployments to override the image via `ISHTI_SANDBOX_IMAGE` if custom internal registries are required.
3. **Maintainer Documentation**: Clarified the exact command needed to update the digest in the future (`docker buildx imagetools inspect`).

---

## 3. Verification & Testing

Added a dedicated test in `tests/skills/sandbox/test_sandbox.py` verifying that the container image is strictly pinned by SHA-256 digest:

```python
def test_image_is_pinned_by_digest():
    assert "@sha256:" in sbx.IMAGE
    assert sbx.IMAGE.startswith("python:3.12-slim@sha256:")
```

### Test Results

```bash
$ python3 -m pytest tests/skills/sandbox/test_sandbox.py
............                                                             [100%]
12 passed in 0.36s
```

All 12 sandbox unit tests passed cleanly.
