"""
FixLoop: A Free, Research-Grade Self-Correcting AI Coding Assistant
with Optimization, Hinting, and Execution Support
"""
import os
import sys
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from contextlib import asynccontextmanager
from backend.api.services.cache_services import cache_manager
from backend.api.routes import code, ide, cache, terminal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Define lifespan context manager for app startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logger.info("Loading cache from disk...")
        cache_manager.load_cache_from_disk()
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
    yield
    try:
        logger.info("Saving cache to disk before shutdown...")
        cache_manager.save_cache_to_disk()
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")

app = FastAPI(
    title="FixLoop",
    description="A Free, Research-Grade Self-Correcting AI Coding Assistant",
    version="1.0.0",
    lifespan=lifespan
)

# Environment variables with defaults
# STATIC_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend", "public"))
# os.makedirs(STATIC_DIR, exist_ok=True)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (not needed in dev)
# app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# @app.get("/")
# async def root():
#     try:
#         return FileResponse(os.path.join(STATIC_DIR, "index.html"), media_type="text/html")
#     except Exception as e:
#         logger.error(f"Error serving index.html: {str(e)}")
#         return HTMLResponse(content="Internal Server Error", status_code=500)

# @app.get("/favicon.ico")
# async def favicon():
#     try:
#         return FileResponse(os.path.join(STATIC_DIR, "favicon.ico"), media_type="image/x-icon")
#     except Exception as e:
#         logger.error(f"Error serving favicon.ico: {str(e)}")
#         return HTMLResponse(status_code=404)

# Include routers
app.include_router(code.router)
app.include_router(ide.router)
app.include_router(cache.router)
app.include_router(terminal.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.api.fixloop:app", host="127.0.0.1", port=8000, reload=True)
    