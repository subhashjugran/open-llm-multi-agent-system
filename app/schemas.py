from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    goal: str = Field(..., min_length=10, description="The business or technical goal for the agents")
    context: str = Field(default="", description="Optional extra context from the user")


class PlanStep(BaseModel):
    step_id: int = Field(..., ge=1)
    title: str
    purpose: str
    research_query: str
    deliverable: str


class ExecutionPlan(BaseModel):
    objective: str
    assumptions: list[str] = Field(default_factory=list)
    steps: list[PlanStep] = Field(default_factory=list)
    success_criteria: list[str] = Field(default_factory=list)


class WebEvidence(BaseModel):
    rank: int = Field(..., ge=1)
    title: str
    url: str
    snippet: str = ""
    content_excerpt: str = ""


class StepExecution(BaseModel):
    step: PlanStep
    evidence: list[WebEvidence] = Field(default_factory=list)
    research_note: str
    output: str = ""


class ReviewResult(BaseModel):
    approved: bool
    feedback: str = ""
    missing_points: list[str] = Field(default_factory=list)


class RunMetrics(BaseModel):
    planning_seconds: float
    research_seconds: float
    execution_seconds: float
    critique_seconds: float = 0.0
    total_seconds: float


class AgentRun(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    run_id: str
    goal: str
    context: str = ""
    plan: ExecutionPlan
    steps: list[StepExecution]
    draft_answer: str
    final_answer: str
    critique: ReviewResult | None = None
    metrics: RunMetrics
    created_at: datetime
    models: dict[str, str] = Field(default_factory=dict)


class RunSummary(BaseModel):
    run_id: str
    goal: str
    created_at: datetime | str
    total_seconds: float


class HealthResponse(BaseModel):
    api_status: str = "ok"
    ollama_status: str
    ollama_models: list[str] = Field(default_factory=list)
    configured_models: dict[str, str] = Field(default_factory=dict)


JSONSchema = dict[str, Any]
