"""Offline test fixtures: no Ollama, no Docker and no running server are needed."""
import os
import sys
import tempfile

# Must be set before the cache module is imported so tests never touch the committed cache files.
os.environ.setdefault("FIXLOOP_CACHE_DIR", tempfile.mkdtemp(prefix="fixloop_cache_"))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

import pytest
from fastapi.testclient import TestClient

import backend.api.services.code_services as code_services
import backend.api.services.logic_services as logic_services
from backend.main import app

FAKE_LLM_REPLY = """Optimization Summary: faster.

Performance Impact: O(n)

Key Optimizations:
- simpler

Optimized Code:
```python
def f(x):
    return x
```
Explanation:
Division by zero removed.

Bugs Found:
- BUG: divides by zero
- FIX: removed the division

Fixed Code:
```python
def f(x):
    return x
```
ERRORS:
- SYNTAX - [LINE 1]: something is wrong
  * IMPACT: high
  * FIX: change it
WARNINGS:
- STYLE - [LINE 2]: could be nicer
SUGGESTIONS:
- add type hints
"""


@pytest.fixture
def prompts(monkeypatch):
    """Replace the LLM with a canned reply and record every prompt that was sent to it."""
    seen = []

    async def fake_generate(prompt, *args, **kwargs):
        seen.append(prompt)
        return FAKE_LLM_REPLY

    async def available():
        return True

    monkeypatch.setattr(logic_services, "ollama_generate", fake_generate)
    monkeypatch.setattr(logic_services, "check_ollama_available", available)
    monkeypatch.setattr(code_services, "check_ollama_available", available)
    return seen


@pytest.fixture
def client():
    return TestClient(app)
