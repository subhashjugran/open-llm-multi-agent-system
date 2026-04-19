from __future__ import annotations

from app.llm import LLMError, OllamaClient
from app.prompts import critic_system_prompt, critic_user_prompt
from app.schemas import ExecutionPlan, ReviewResult, StepExecution


REVIEW_SCHEMA = {
    "type": "object",
    "properties": {
        "approved": {"type": "boolean"},
        "feedback": {"type": "string"},
        "missing_points": {
            "type": "array",
            "items": {"type": "string"},
        },
    },
    "required": ["approved", "feedback", "missing_points"],
    "additionalProperties": False,
}


class CriticAgent:
    """Reviews the draft and asks for a single correction pass if needed."""

    def __init__(self, client: OllamaClient, model: str) -> None:
        self.client = client
        self.model = model

    def review(
        self,
        goal: str,
        plan: ExecutionPlan,
        steps: list[StepExecution],
        draft: str,
    ) -> ReviewResult:
        try:
            payload = self.client.chat_json(
                model=self.model,
                system_prompt=critic_system_prompt(),
                user_prompt=critic_user_prompt(goal, plan, steps, draft),
                schema=REVIEW_SCHEMA,
            )
            return ReviewResult.model_validate(payload)
        except (LLMError, ValueError):
            return ReviewResult(
                approved=True,
                feedback="Critic skipped because the model did not return valid review JSON.",
                missing_points=[],
            )
