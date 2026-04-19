from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.config import get_settings
from app.orchestrator import build_orchestrator
from app.schemas import AgentRun, ChatRequest, HealthResponse

BASE_DIR = Path(__file__).resolve().parents[1]
INDEX_FILE = BASE_DIR / "static" / "index.html"

settings = get_settings()
orchestrator = build_orchestrator(settings)

app = FastAPI(
    title="Open LLM Multi-Agent System",
    version="0.1.0",
    description="Planner + Researcher + Executor + Critic powered by Ollama and free web search.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def index() -> str:
    return INDEX_FILE.read_text(encoding="utf-8")


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return orchestrator.health()


@app.post("/api/execute", response_model=AgentRun)
def execute(request: ChatRequest) -> AgentRun:
    try:
        return orchestrator.run(request.goal, request.context)
    except Exception as exc:  # pragma: no cover - API defensive layer
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/runs", response_model=list)
def list_runs(limit: int = Query(default=10, ge=1, le=50)):
    return orchestrator.list_runs(limit)


@app.get("/api/runs/{run_id}", response_model=AgentRun)
def get_run(run_id: str) -> AgentRun:
    try:
        return orchestrator.get_run(run_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
