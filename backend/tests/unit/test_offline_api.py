import json

import docker
import pytest

import backend.api.routes.terminal as terminal
import backend.api.services.code_services as code_services
import backend.api.services.logic_services as logic_services
from backend.api.services.cache_services import cache_manager

BUGGY = "def f(x):\n    return x/0\nprint(f(1))"


# ---------- validation ----------
def test_empty_code_rejected(client):
    assert client.post("/api/code", json={"code": "  "}).status_code == 400


def test_unsupported_language_rejected(client):
    assert client.post("/api/code", json={"code": "x", "language": "cobol"}).status_code == 400


def test_ollama_down_returns_503(client, monkeypatch):
    async def down():
        return False

    monkeypatch.setattr(code_services, "check_ollama_available", down)
    assert client.post("/api/code", json={"code": BUGGY, "action": "analyze"}).status_code == 503


# ---------- code execution ----------
def test_execute_prints(client):
    r = client.post("/api/code", json={"code": "print(2+2)", "action": "execute"})
    assert r.status_code == 200
    assert r.json()["execution_result"]["stdout"].strip() == "4"


def test_execute_with_inputs(client):
    code = "n = input('n:')\nprint(int(n) * 2)"
    r = client.post("/api/code", json={"code": code, "action": "execute", "inputs": ["21"]})
    assert "42" in r.json()["execution_result"]["stdout"]


# ---------- LLM actions (fake LLM) ----------
@pytest.mark.parametrize("action", ["analyze", "optimize", "hint", "fix"])
def test_llm_actions(client, prompts, action):
    r = client.post("/api/code", json={"code": BUGGY, "action": action})
    assert r.status_code == 200
    assert prompts, "the LLM should have been called"


def test_fix_returns_code_and_attempts(client, prompts):
    body = client.post("/api/code", json={"code": BUGGY, "action": "fix"}).json()
    assert "def f(x)" in body["processed_code"]
    assert body["verified"] is True
    assert body["attempts"][0]["ok"] is True


def test_batch_processes_all_items(client, prompts):
    r = client.post("/api/code/batch", json={"codes": [BUGGY, "print(1)"], "action": "analyze"})
    assert r.status_code == 200
    assert r.json()["count"] == 2


def test_batch_rejects_empty_items_with_readable_message(client):
    r = client.post("/api/code/batch", json={"codes": [BUGGY, "   "], "action": "analyze"})
    assert r.status_code == 400
    assert "non-empty" in r.json()["error"]  # not a comma-separated string of characters


def test_analyze_buckets_issues_by_section(client, prompts):
    body = client.post("/api/code", json={"code": BUGGY, "action": "analyze"}).json()
    assert any("something is wrong" in e for e in body["errors"])
    assert any("could be nicer" in w for w in body["warnings"])
    assert any("type hints" in s for s in body["suggestions"])


# ---------- IDE endpoint regressions ----------
def test_ide_analyze_surfaces_errors(client, prompts):
    body = client.post("/api/ide/analyze", json={"code": BUGGY, "action": "analyze"}).json()
    assert body["errors"], "errors found by the analysis must reach the IDE response"
    assert body["inline_diagnostics"]


def test_ide_execute_returns_output(client):
    body = client.post("/api/ide/analyze", json={"code": "print('hi')", "action": "execute"}).json()
    assert body["execution_result"]["stdout"].strip() == "hi"
    assert body["errors"] == []


def test_ide_execute_reports_failures(client):
    body = client.post("/api/ide/analyze", json={"code": "1/0", "action": "execute"}).json()
    assert body["errors"] and "ZeroDivisionError" in body["errors"][0]


# ---------- self-correction ----------
@pytest.mark.asyncio
async def test_self_correcting_retries_on_syntax_error(monkeypatch):
    replies = iter([
        "Explanation:\nbroken\n\nFixed Code:\n```python\ndef f(:\n    pass\n```",
        "Explanation:\nok\n\nFixed Code:\n```python\ndef f():\n    return 1\n```",
    ])
    prompts = []

    async def fake_generate(prompt, *a, **k):
        prompts.append(prompt)
        return next(replies)

    monkeypatch.setattr(logic_services, "ollama_generate", fake_generate)
    result = await logic_services.fix_code_self_correcting("def f():\n    return 1/0", "python")
    assert [a["ok"] for a in result["attempts"]] == [False, True]
    assert result["verified"] is True
    assert "SyntaxError" in prompts[1], "the failure must be fed back to the model"


@pytest.mark.asyncio
async def test_self_correcting_gives_up_after_max_attempts(monkeypatch):
    async def always_broken(prompt, *a, **k):
        return "Explanation:\nx\n\nFixed Code:\n```python\ndef f(:\n```"

    monkeypatch.setattr(logic_services, "ollama_generate", always_broken)
    result = await logic_services.fix_code_self_correcting("def f():\n    pass", "python", max_attempts=2)
    assert len(result["attempts"]) == 2
    assert result["verified"] is False


# ---------- context-aware fix ----------
def test_fix_with_context_sends_context(client, prompts):
    r = client.post("/api/code/fix-with-context", json={
        "code": BUGGY,
        "context": "helper module defines CONSTANT",
        "error_message": "ZeroDivisionError: division by zero",
        "dependencies": ["numpy"],
    })
    assert r.status_code == 200
    sent = prompts[0]
    assert "helper module defines CONSTANT" in sent
    assert "ZeroDivisionError" in sent
    assert "numpy" in sent


# ---------- streaming ----------
def test_stream_emits_chunks(client, monkeypatch):
    async def available():
        return True

    async def fake_stream(prompt, model, max_tokens, *a, **k):
        for piece in ["Hel", "lo"]:
            yield piece

    monkeypatch.setattr(code_services, "check_ollama_available", available)
    monkeypatch.setattr(code_services, "ollama_stream", fake_stream)
    r = client.post("/api/code/stream", json={"code": BUGGY, "action": "analyze"})
    events = [json.loads(line) for line in r.text.splitlines() if line.strip()]
    assert events[0]["type"] == "start" and events[-1]["type"] == "end"
    assert "".join(e["content"] for e in events if e["type"] == "chunk") == "Hello"


# ---------- cache ----------
def test_cache_roundtrip_and_clear(client):
    key = cache_manager.make_key("model", "prompt")
    assert cache_manager.get(key) is None
    cache_manager.set(key, "answer")
    assert cache_manager.get(key) == "answer"
    stats = client.get("/api/cache/stats").json()
    assert stats["cache_summary"]["total_entries"] >= 1
    r = client.post("/api/cache/clear")
    assert r.status_code == 200 and r.json()["success"] is True
    assert cache_manager.get(key) is None


@pytest.mark.asyncio
async def test_ollama_generate_uses_cache(monkeypatch):
    calls = []

    class FakeResponse:
        status_code = 200

        def json(self):
            return {"response": "cached text"}

    class FakeClient:
        def __init__(self, *a, **k):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            return False

        async def post(self, *a, **k):
            calls.append(1)
            return FakeResponse()

    monkeypatch.setattr(logic_services.httpx, "AsyncClient", FakeClient)
    cache_manager.clear_cache()
    first = await logic_services.ollama_generate("unique prompt 123", "llama3", 64)
    second = await logic_services.ollama_generate("unique prompt 123", "llama3", 64)
    assert first == second == "cached text"
    assert len(calls) == 1


# ---------- terminal without Docker ----------
def test_terminal_without_docker(client, monkeypatch):
    def no_docker():
        raise docker.errors.DockerException("daemon not running")

    monkeypatch.setattr(terminal, "get_docker_client", no_docker)
    with client.websocket_connect("/ws/terminal") as ws:
        assert "Docker is not running" in ws.receive_text()
