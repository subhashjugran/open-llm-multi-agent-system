import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from app.config import Settings
from app.orchestrator import MultiAgentOrchestrator
from app.schemas import ExecutionPlan, PlanStep, ReviewResult, RunMetrics, StepExecution
from app.storage.run_store import FileRunStore


class DummyPlanner:
    def plan(self, goal: str, context: str = "") -> ExecutionPlan:
        return ExecutionPlan(
            objective=goal,
            steps=[
                PlanStep(
                    step_id=1,
                    title="Research core trade-offs",
                    purpose="Gather evidence",
                    research_query=goal,
                    deliverable="Key insights",
                )
            ],
            success_criteria=["Grounded answer", "Practical next steps"],
        )


class DummyResearcher:
    def execute(self, step: PlanStep) -> StepExecution:
        return StepExecution(step=step, research_note="Evidence summary", output="Evidence summary")


class DummyExecutor:
    def __init__(self):
        self.calls = 0

    def execute(self, goal, context, plan, steps, revision_feedback: str = "") -> str:
        self.calls += 1
        if revision_feedback:
            return f"revised answer for {goal}"
        return f"draft answer for {goal}"


class DummyCritic:
    def review(self, goal, plan, steps, draft) -> ReviewResult:
        return ReviewResult(approved=False, feedback="Add more practical next steps", missing_points=["Rollout plan"])


class DummyLLMClient:
    def list_models(self):
        return ["llama3.2:3b"]


class OrchestratorTests(unittest.TestCase):
    def test_full_run_with_revision(self):
        with tempfile.TemporaryDirectory() as tmp:
            settings = Settings(output_dir=Path(tmp))
            executor = DummyExecutor()
            orchestrator = MultiAgentOrchestrator(
                planner=DummyPlanner(),
                researcher=DummyResearcher(),
                executor=executor,
                critic=DummyCritic(),
                run_store=FileRunStore(Path(tmp)),
                settings=settings,
                llm_client=DummyLLMClient(),
            )
            run = orchestrator.run("Design a practical event-driven architecture")
            self.assertEqual(run.goal, "Design a practical event-driven architecture")
            self.assertTrue(run.final_answer.startswith("revised answer"))
            self.assertEqual(executor.calls, 2)
            self.assertEqual(len(orchestrator.list_runs()), 1)


if __name__ == "__main__":
    unittest.main()
