import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import code, terminal, ide, cache
from backend.api.services.cache_services import cache_manager

logger = logging.getLogger(__name__)

# Origins allowed to call the API from a browser. Override with a comma-separated list, e.g.
#   FIXLOOP_CORS_ORIGINS="https://my-frontend.example.com"
# "null" covers pages opened from a file:// URL.
DEFAULT_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "null",
]
ALLOWED_ORIGINS = [
    o.strip() for o in os.getenv("FIXLOOP_CORS_ORIGINS", ",".join(DEFAULT_ORIGINS)).split(",") if o.strip()
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        cache_manager.load_cache_from_disk()
    except Exception as e:  # a corrupt cache must never stop the API from starting
        logger.error("Could not load cache from disk: %s", e)
    yield
    try:
        cache_manager.save_cache_to_disk()
    except Exception as e:
        logger.error("Could not save cache to disk: %s", e)


app = FastAPI(
    title="FixLoop",
    description="A free, local AI coding assistant: analyze, fix, optimize, hint and run code.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(code.router)
app.include_router(terminal.router)
app.include_router(ide.router)
app.include_router(cache.router)


@app.get("/api/health")
async def health():
    """Liveness check; also reports whether Ollama is reachable."""
    from backend.api.services.logic_services import check_ollama_available

    return {"status": "ok", "ollama": await check_ollama_available()}


if __name__ == "__main__":
    import uvicorn

    # Code execution is not sandboxed, so only listen on localhost unless told otherwise.
    uvicorn.run(app, host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "8000")))
