# Case Study 21: Preserving Query Parameters in LangSmith Gateway Base URLs in LangChain

## Executive Summary

| Attribute | Details |
| :--- | :--- |
| **Target Repository** | [`langchain-ai/langchain`](https://github.com/langchain-ai/langchain) |
| **Pull Request** | [PR #41979: fix(core): preserve query parameters in gateway base URLs](https://github.com/langchain-ai/langchain/pull/41979) |
| **Issue Resolved** | [Issue #41951: Gateway base URLs with query parameters append provider path to query instead of URL path](https://github.com/langchain-ai/langchain/issues/41951) |
| **Component** | `libs/core/langchain_core/utils/_gateway.py` |
| **Author** | **Rishabh Bafna** (`@RishabhIIITD` / `rishabh20118@iiitd.ac.in`) |
| **Status** | 🔴 Closed by triage bot (LangChain `check-issue-link` requires maintainer issue assignment prior to PR acceptance) |
| **Test Verification** | 100% unit tests passing in `libs/core/tests/unit_tests/utils/test_gateway.py` (64/64 passed) |

---

## 1. Problem Statement

The [LangSmith LLM gateway](https://docs.langchain.com/langsmith/llm-gateway) in `langchain-core` enables chat models to route outbound requests to LLM providers (such as OpenAI, Anthropic, Fireworks) through proxies configured via environment variables (`LANGSMITH_GATEWAY`) or programmatic context managers (`langsmith_gateway`).

When a gateway context was configured with a custom base URL containing query parameters (e.g. `https://gateway.example.test/proxy?tenant=demo`), `_gateway.py` naively string-concatenated the provider path (`openai/v1`) directly to the end of the base URL:

```python
# Previous implementation:
return f"{override.base_url}/{provider_path}"
```

### Impact & Bug Manifestation:

```python
with langsmith_gateway(
    api_key="placeholder",
    base_url="https://gateway.example.test/proxy?tenant=demo",
):
    config = _resolve_gateway_config(
        base_url=None,
        api_key=None,
        provider_path="openai/v1",
    )

print(config.base_url)
# Actual output:
# https://gateway.example.test/proxy?tenant=demo/openai/v1
# Path:  /proxy
# Query: tenant=demo/openai/v1
```

Instead of targeting `/proxy/openai/v1` with query `tenant=demo`, the provider path was mangled directly into the query string value, resulting in corrupted routing, HTTP 404s, or proxy rejection on multi-tenant gateways.

---

## 2. Root Cause Analysis

In `libs/core/langchain_core/utils/_gateway.py`:
1. `_override_base_url` performed:
   ```python
   return f"{override.base_url}/{provider_path}"
   ```
2. `_resolve_gateway_base_url` performed:
   ```python
   return f"{base}/{provider_path}"
   ```
Both functions assumed that `base_url` only contained a path without query strings or fragments. Under standard RFC 3986 URL parsing, query strings (`?`) must follow the complete URL path component.

---

## 3. Technical Implementation

We implemented a dedicated URL path joiner using Python's standard `urllib.parse` utilities (`urlsplit`, `urlunsplit`):

```python
def _join_gateway_url(base_url: str, provider_path: str) -> str:
    """Append a provider path segment to a base URL, preserving query and fragment."""
    parsed = urlsplit(base_url)
    clean_path = parsed.path.rstrip("/")
    sub_path = provider_path.lstrip("/")
    new_path = f"{clean_path}/{sub_path}" if clean_path else f"/{sub_path}"
    return urlunsplit(
        (parsed.scheme, parsed.netloc, new_path, parsed.query, parsed.fragment)
    )
```

And updated `_override_base_url` and `_resolve_gateway_base_url` to use `_join_gateway_url`:

```python
def _override_base_url(
    override: _GatewayOverride, base_url: str | None, provider_path: str
) -> str:
    candidate = _join_gateway_url(override.base_url, provider_path)
    if isinstance(base_url, str):
        parsed_base = urlsplit(base_url)
        parsed_override = urlsplit(override.base_url)
        if (
            parsed_base.scheme == parsed_override.scheme
            and parsed_base.netloc == parsed_override.netloc
            and (
                parsed_base.path.startswith(f"{parsed_override.path.rstrip('/')}/")
                or base_url.startswith(f"{override.base_url}/")
            )
        ):
            return base_url
    return candidate
```

---

## 4. Testing & Verification

Added two comprehensive unit tests to `libs/core/tests/unit_tests/utils/test_gateway.py`:

```python
def test_gateway_base_url_with_query_params() -> None:
    """A gateway base URL with query params appends provider path to path, not query."""
    custom_gateway = "https://gateway.example.test/proxy?tenant=demo"
    with langsmith_gateway(api_key="ctx-key", base_url=custom_gateway):
        config = _config()
    assert config.base_url == "https://gateway.example.test/proxy/openai/v1?tenant=demo"


def test_gateway_env_with_query_params(monkeypatch: pytest.MonkeyPatch) -> None:
    """LANGSMITH_GATEWAY env var with query params preserves query parameters."""
    monkeypatch.setenv(
        "LANGSMITH_GATEWAY", "https://gateway.example.test/proxy?tenant=demo"
    )
    monkeypatch.setenv("LANGSMITH_GATEWAY_API_KEY", "env-key")
    config = _config()
    assert config.base_url == "https://gateway.example.test/proxy/openai/v1?tenant=demo"
```

### Execution Results:
```bash
$ pytest libs/core/tests/unit_tests/utils/test_gateway.py
============================== 64 passed in 0.05s ==============================
$ ruff check libs/core/langchain_core/utils/_gateway.py libs/core/tests/unit_tests/utils/test_gateway.py
All checks passed!
$ ruff format --check libs/core/langchain_core/utils/_gateway.py libs/core/tests/unit_tests/utils/test_gateway.py
2 files already formatted
```

---

## 5. Key Engineering Takeaways

1. **RFC 3986 Conformance**: Never perform naive string concatenation (`f"{base}/{subpath}"`) on user-provided base URLs; always separate scheme, authority, path, query, and fragment components.
2. **Context-Aware Overrides**: Gateways and proxy routing must support multi-tenant query parameters (`?tenant=...`, `?org=...`) without corrupting downstream provider endpoints.
