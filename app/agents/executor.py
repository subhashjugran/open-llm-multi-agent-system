from __future__ import annotations

from app.llm import OllamaClient
from app.prompts import executor_system_prompt, executor_user_prompt
from app.schemas import ExecutionPlan, StepExecution


class ExecutorAgent:
    """Turns the plan and step research into the final response."""

    def __init__(self, client: OllamaClient, model: str) -> None:
        self.client = client
        self.model = model

    def execute(
        self,
        goal: str,
        context: str,
        plan: ExecutionPlan,
        steps: list[StepExecution],
        revision_feedback: str = "",
    ) -> str:
        return self.client.chat(
            model=self.model,
            system_prompt=executor_system_prompt(),
            user_prompt=executor_user_prompt(goal, context, plan, steps, revision_feedback),
            temperature=0.2,
        )
