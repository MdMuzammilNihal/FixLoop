from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import code, terminal, ide, cache

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(code.router)
app.include_router(terminal.router)
app.include_router(ide.router)
app.include_router(cache.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 