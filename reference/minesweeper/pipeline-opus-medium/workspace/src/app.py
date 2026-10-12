"""
FastAPI Main Application Entrypoint — Instant OpenAPI Generator.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.entrypoints.routers.game import router as game_router
from src.entrypoints.routers.difficulty import router as difficulty_router
from src.entrypoints.routers.best_time import router as best_time_router

app = FastAPI(
    title="Generated Enterprise Domain API",
    description="Deterministic Domain-Driven API automatically projected from domain models.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(game_router)
app.include_router(difficulty_router)
app.include_router(best_time_router)

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "domain-api"}
