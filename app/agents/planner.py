from __future__ import annotations

from app.llm import OllamaClient
from app.prompts import planner_system_prompt, planner_user_prompt
from app.schemas import ExecutionPlan, PlanStep


class PlannerAgent:
    """Turns a user goal into a structured execution plan."""

    def __init__(self, client: OllamaClient, model: str, max_steps: int) -> None:
        self.client = client
        self.model = model
        self.max_steps = max_steps

    def plan(self, goal: str, context: str = "") -> ExecutionPlan:
        payload = self.client.chat_json(
            model=self.model,
            system_prompt=planner_system_prompt(self.max_steps),
            user_prompt=planner_user_prompt(goal, context),
            schema=ExecutionPlan.model_json_schema(),
        )
        plan = ExecutionPlan.model_validate(payload)
        normalized_steps: list[PlanStep] = []
        for index, step in enumerate(plan.steps[: self.max_steps], start=1):
            normalized_steps.append(step.model_copy(update={"step_id": index}))
        if not normalized_steps:
            normalized_steps.append(
                PlanStep(
                    step_id=1,
                    title="Clarify the request",
                    purpose="Understand the user's objective and expected output.",
                    research_query=goal,
                    deliverable="A concise interpretation of the goal",
                )
            )
        return plan.model_copy(update={"steps": normalized_steps})
