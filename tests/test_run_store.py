import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from app.schemas import AgentRun, ExecutionPlan, PlanStep, RunMetrics, StepExecution
from app.storage.run_store import FileRunStore


class RunStoreTests(unittest.TestCase):
    def test_save_and_load(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = FileRunStore(Path(tmp))
            run = AgentRun(
                run_id="demo-run",
                goal="test goal",
                context="",
                plan=ExecutionPlan(
                    objective="test goal",
                    steps=[
                        PlanStep(
                            step_id=1,
                            title="Step 1",
                            purpose="Test purpose",
                            research_query="test query",
                            deliverable="test deliverable",
                        )
                    ],
                ),
                steps=[
                    StepExecution(
                        step=PlanStep(
                            step_id=1,
                            title="Step 1",
                            purpose="Test purpose",
                            research_query="test query",
                            deliverable="test deliverable",
                        ),
                        research_note="A note",
                    )
                ],
                draft_answer="draft",
                final_answer="final",
                metrics=RunMetrics(
                    planning_seconds=0.1,
                    research_seconds=0.2,
                    execution_seconds=0.3,
                    critique_seconds=0.0,
                    total_seconds=0.6,
                ),
                created_at=datetime.now(timezone.utc),
                models={"planner": "llama3.2:3b"},
            )
            store.save(run)
            loaded = store.load("demo-run")
            self.assertEqual(loaded.run_id, "demo-run")
            self.assertEqual(loaded.final_answer, "final")
            self.assertEqual(len(store.list_runs()), 1)


if __name__ == "__main__":
    unittest.main()
