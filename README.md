# FixLoop

A free, local AI coding assistant. Paste code to **analyze**, **fix**, **optimize** or get **hints**, or
**run** it. All LLM work is done by [Ollama](https://ollama.com) on your machine, with no API keys.

Fixes are self-correcting: each proposed fix is checked (Python syntax, optionally by running it), and on
failure the error is sent back to the model for another attempt, up to 3 tries.

## Requirements

- Python 3.10+, Node.js 18+
- [Ollama](https://ollama.com/download) with the `llama3` model
- Docker (optional, for the in-browser Python terminal)

```bash
ollama pull llama3
```

## Run

Backend, from the repository root:

```bash
python -m venv venv
venv\Scripts\activate          # macOS/Linux: source venv/bin/activate
pip install -r backend/requirements.txt
python -m uvicorn backend.main:app --port 8000
```

API docs: http://localhost:8000/docs

Frontend, in a second terminal:

```bash
cd frontend-react
npm install
npm run dev
```

Open the URL Vite prints (usually http://localhost:5173). `/api` is proxied to port 8000.

Docker (backend + Ollama):

```bash
docker compose -f docker/docker-compose.yml up --build
docker compose -f docker/docker-compose.yml exec ollama ollama pull llama3
```

## API

| Endpoint | Purpose |
|---|---|
| `POST /api/code` | `action`: `analyze`, `optimize`, `hint`, `fix`, `execute`. `verify_execution: true` also runs each fix |
| `POST /api/code/stream` | Streamed (JSON lines) analyze/optimize/fix/hint |
| `POST /api/code/batch` | Several snippets in one call |
| `POST /api/code/fix-with-context` | Fix using `context`, `error_message`, `dependencies` |
| `POST /api/ide/analyze` | Editor-oriented variant with inline diagnostics |
| `GET /api/cache/stats`, `POST /api/cache/save`, `POST /api/cache/clear` | LLM response cache |
| `GET /api/health` | Liveness and Ollama reachability |
| `WS /ws/terminal` | Python REPL in a Docker container |

## Configuration

Optional environment variables: `OLLAMA_BASE_URL` (`http://localhost:11434`), `OLLAMA_MODEL` (`llama3`),
`FIXLOOP_TEMPERATURE` (`0.2`), `HOST` (`127.0.0.1`), `PORT` (`8000`), `FIXLOOP_CORS_ORIGINS`.
See `docker/env.example`.

## Tests and benchmark

```bash
pytest                                            # offline unit tests, no Ollama or Docker needed
cd frontend-react && npm run typecheck
python -m backend.benchmark.run_benchmark         # 40 buggy snippets with hidden tests (needs Ollama)
```

Benchmark results are written to `backend/benchmark/results/`.

## Layout

- `backend/main.py`: FastAPI app; routes in `backend/api/routes`, logic in `backend/api/services`
- `backend/api/services/logic_services.py`: prompts, parsing, execution, self-correcting fix loop
- `backend/api/services/cache_services.py`: response cache
- `backend/benchmark/`: benchmark cases and runner
- `backend/tests/unit/`: offline tests run by CI
- `frontend-react/`: React, TypeScript and Monaco editor UI
