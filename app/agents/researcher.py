from __future__ import annotations

from app.llm import OllamaClient
from app.prompts import researcher_system_prompt, researcher_user_prompt
from app.schemas import PlanStep, StepExecution, WebEvidence
from app.tools import PageFetcher, WebSearchTool


class ResearchAgent:
    """Uses search and page fetching tools to gather evidence per plan step."""

    def __init__(
        self,
        client: OllamaClient,
        model: str,
        search_tool: WebSearchTool,
        page_fetcher: PageFetcher,
        max_pages_per_step: int = 2,
        fetch_url_content: bool = True,
    ) -> None:
        self.client = client
        self.model = model
        self.search_tool = search_tool
        self.page_fetcher = page_fetcher
        self.max_pages_per_step = max_pages_per_step
        self.fetch_url_content = fetch_url_content

    def execute(self, step: PlanStep) -> StepExecution:
        try:
            evidence = self.search_tool.search(step.research_query)
        except Exception as exc:  # pragma: no cover - defensive fallback for tool failures
            return StepExecution(
                step=step,
                evidence=[],
                research_note=(
                    "Research failed because the web search tool was unavailable. "
                    f"Error: {exc}"
                ),
                output="",
            )

        enriched: list[WebEvidence] = []
        for item in evidence:
            content_excerpt = item.content_excerpt
            if self.fetch_url_content and item.rank <= self.max_pages_per_step:
                content_excerpt = self.page_fetcher.fetch_excerpt(item.url)
            enriched.append(item.model_copy(update={"content_excerpt": content_excerpt}))

        if not enriched:
            return StepExecution(
                step=step,
                evidence=[],
                research_note="No evidence was returned for this step.",
                output="",
            )

        research_note = self.client.chat(
            model=self.model,
            system_prompt=researcher_system_prompt(),
            user_prompt=researcher_user_prompt(step, enriched),
            temperature=0.1,
        )
        return StepExecution(
            step=step,
            evidence=enriched,
            research_note=research_note,
            output=research_note,
        )
