from __future__ import annotations

import time
from datetime import datetime, timezone
from uuid import uuid4

from app.agents import CriticAgent, ExecutorAgent, PlannerAgent, ResearchAgent
from app.config import Settings, get_settings
from app.llm import OllamaClient
from app.schemas import AgentRun, HealthResponse, ReviewResult, RunMetrics
from app.storage import FileRunStore
from app.tools import PageFetcher, WebSearchTool


class MultiAgentOrchestrator:
    """Coordinates the Planner -> Researcher -> Executor -> Critic workflow."""

    def __init__(
        self,
        planner: PlannerAgent,
        researcher: ResearchAgent,
        executor: ExecutorAgent,
        critic: CriticAgent | None,
        run_store: FileRunStore,
        settings: Settings,
        llm_client: OllamaClient,
    ) -> None:
        self.planner = planner
        self.researcher = researcher
        self.executor = executor
        self.critic = critic
        self.run_store = run_store
        self.settings = settings
        self.llm_client = llm_client

    def health(self) -> HealthResponse:
        models = self.llm_client.list_models()
        return HealthResponse(
            ollama_status="ok" if models else "down",
            ollama_models=models,
            configured_models={
                "planner": self.settings.planner_model,
                "researcher": self.settings.researcher_model,
                "executor": self.settings.executor_model,
                "critic": self.settings.critic_model,
            },
        )

    def run(self, goal: str, context: str = "") -> AgentRun:
        total_start = time.perf_counter()
        run_id = f"{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}-{uuid4().hex[:8]}"

        planning_start = time.perf_counter()
        plan = self.planner.plan(goal, context)
        planning_seconds = time.perf_counter() - planning_start

        research_start = time.perf_counter()
        step_outputs = [self.researcher.execute(step) for step in plan.steps]
        research_seconds = time.perf_counter() - research_start

        execution_start = time.perf_counter()
        draft = self.executor.execute(goal, context, plan, step_outputs)
        execution_seconds = time.perf_counter() - execution_start

        critique_seconds = 0.0
        critique: ReviewResult | None = None
        final_answer = draft

        if self.critic is not None:
            critique_start = time.perf_counter()
            critique = self.critic.review(goal, plan, step_outputs, draft)
            critique_seconds = time.perf_counter() - critique_start
            if not critique.approved:
                feedback_parts = [critique.feedback.strip()]
                if critique.missing_points:
                    feedback_parts.append("Missing points: " + "; ".join(critique.missing_points))
                revision_feedback = "\n".join(part for part in feedback_parts if part)
                revision_start = time.perf_counter()
                final_answer = self.executor.execute(
                    goal=goal,
                    context=context,
                    plan=plan,
                    steps=step_outputs,
                    revision_feedback=revision_feedback,
                )
                execution_seconds += time.perf_counter() - revision_start

        metrics = RunMetrics(
            planning_seconds=planning_seconds,
            research_seconds=research_seconds,
            execution_seconds=execution_seconds,
            critique_seconds=critique_seconds,
            total_seconds=time.perf_counter() - total_start,
        )

        run = AgentRun(
            run_id=run_id,
            goal=goal,
            context=context,
            plan=plan,
            steps=step_outputs,
            draft_answer=draft,
            final_answer=final_answer,
            critique=critique,
            metrics=metrics,
            created_at=datetime.now(timezone.utc),
            models={
                "planner": self.settings.planner_model,
                "researcher": self.settings.researcher_model,
                "executor": self.settings.executor_model,
                "critic": self.settings.critic_model if self.critic else "disabled",
            },
        )
        self.run_store.save(run)
        return run

    def get_run(self, run_id: str) -> AgentRun:
        return self.run_store.load(run_id)

    def list_runs(self, limit: int = 10):
        return self.run_store.list_runs(limit)


def build_orchestrator(settings: Settings | None = None) -> MultiAgentOrchestrator:
    settings = settings or get_settings()
    llm_client = OllamaClient(
        base_url=settings.ollama_base_url,
        timeout=settings.request_timeout,
        keep_alive=settings.keep_alive,
    )
    search_tool = WebSearchTool(
        max_results=settings.max_search_results,
        region=settings.web_region,
    )
    page_fetcher = PageFetcher(
        timeout=20,
        max_chars=settings.max_extract_chars,
        user_agent=settings.user_agent,
    )
    run_store = FileRunStore(settings.output_dir)

    planner = PlannerAgent(llm_client, settings.planner_model, settings.max_steps)
    researcher = ResearchAgent(
        client=llm_client,
        model=settings.researcher_model,
        search_tool=search_tool,
        page_fetcher=page_fetcher,
        max_pages_per_step=settings.max_pages_per_step,
        fetch_url_content=settings.fetch_url_content,
    )
    executor = ExecutorAgent(llm_client, settings.executor_model)
    critic = CriticAgent(llm_client, settings.critic_model) if settings.enable_critic else None

    return MultiAgentOrchestrator(
        planner=planner,
        researcher=researcher,
        executor=executor,
        critic=critic,
        run_store=run_store,
        settings=settings,
        llm_client=llm_client,
    )
