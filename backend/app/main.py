from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .routers import health, runs, topics

settings = get_settings()

app = FastAPI(title="Automated Newsletter Platform", version="0.1.0")
app.include_router(health.router)
app.include_router(topics.router)
app.include_router(runs.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Newsletter automation backend"}
