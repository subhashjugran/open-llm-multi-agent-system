from __future__ import annotations

from app.schemas import ExecutionPlan, PlanStep, StepExecution, WebEvidence
from app.utils import bullet_list


def planner_system_prompt(max_steps: int) -> str:
    return (
        "You are the Planner agent inside a multi-agent system. "
        "Break the user's goal into the minimum useful set of executable steps. "
        f"Return between 2 and {max_steps} steps. "
        "Every step must have a concrete research query that a search tool can run. "
        "Avoid duplicated work, abstract fluff, and vague wording. "
        "Return JSON only."
    )


def planner_user_prompt(goal: str, context: str) -> str:
    extra = context.strip() or "None"
    return f"""
    Create an execution plan for the goal below.

    Goal:
    {goal}

    Additional context:
    {extra}

    Rules:
    - Assume the executor should produce a final architect-level answer.
    - Keep the plan practical enough to execute with web search and summarization.
    - Prefer fewer, stronger steps over many weak steps.
    - Return JSON only.
    """


def _format_evidence(evidence: list[WebEvidence]) -> str:
    chunks: list[str] = []
    for item in evidence:
        excerpt = item.content_excerpt or "No extracted page content available."
        chunks.append(
            f"[S{item.rank}] {item.title}\n"
            f"URL: {item.url}\n"
            f"Snippet: {item.snippet or 'No snippet'}\n"
            f"Excerpt: {excerpt}"
        )
    return "\n\n".join(chunks) if chunks else "No evidence returned."


def researcher_system_prompt() -> str:
    return (
        "You are the Researcher agent. Convert raw web evidence into a concise, factual note "
        "for the executor. Use only the supplied evidence. Flag contradictions, stale data, or weak evidence."
    )


def researcher_user_prompt(step: PlanStep, evidence: list[WebEvidence]) -> str:
    return f"""
    Research the following step and summarize what matters for the final answer.

    Step title: {step.title}
    Step purpose: {step.purpose}
    Target deliverable: {step.deliverable}

    Evidence:
    {_format_evidence(evidence)}

    Output format:
    1. A short synthesis paragraph.
    2. A bullet list of facts the executor should retain.
    3. Any risks, ambiguity, or missing data.
    """


def _format_plan(plan: ExecutionPlan) -> str:
    items = []
    for step in plan.steps:
        items.append(
            f"{step.step_id}. {step.title}\n"
            f"Purpose: {step.purpose}\n"
            f"Research query: {step.research_query}\n"
            f"Deliverable: {step.deliverable}"
        )
    return "\n\n".join(items)


def _format_step_outputs(steps: list[StepExecution]) -> str:
    sections: list[str] = []
    for item in steps:
        evidence_block = _format_evidence(item.evidence)
        sections.append(
            f"Step {item.step.step_id}: {item.step.title}\n"
            f"Research note:\n{item.research_note}\n\n"
            f"Evidence:\n{evidence_block}"
        )
    return "\n\n".join(sections)


def executor_system_prompt() -> str:
    return (
        "You are the Executor agent. Build the final answer from the plan and the research notes. "
        "Write like a senior architect: direct, structured, and practical. "
        "Do not invent sources or facts that are not present in the supplied evidence. "
        "If evidence is incomplete, say so clearly."
    )


def executor_user_prompt(
    goal: str,
    context: str,
    plan: ExecutionPlan,
    steps: list[StepExecution],
    revision_feedback: str = "",
) -> str:
    revision_section = revision_feedback.strip() or "None"
    context_block = context.strip() or "None"
    return f"""
    Produce the final answer for the user.

    Original goal:
    {goal}

    Additional context:
    {context_block}

    Plan:
    {_format_plan(plan)}

    Step outputs:
    {_format_step_outputs(steps)}

    Reviewer feedback to incorporate:
    {revision_section}

    Required output structure:
    - Title
    - Executive summary
    - Main answer with clear sections
    - Risks and trade-offs
    - Practical next steps
    - Source list using the supplied [Sx] source labels
    """


def critic_system_prompt() -> str:
    return (
        "You are the Critic agent. Review the draft for completeness, grounding, and architectural quality. "
        "Return JSON only. Approve drafts that are solid and practical."
    )


def critic_user_prompt(goal: str, plan: ExecutionPlan, steps: list[StepExecution], draft: str) -> str:
    return f"""
    Review the draft answer.

    Goal:
    {goal}

    Success criteria:
    {bullet_list(plan.success_criteria)}

    Available evidence summary:
    {bullet_list([f'Step {item.step.step_id}: {item.step.title}' for item in steps])}

    Draft:
    {draft}

    Review rules:
    - Approve if the draft answers the goal, uses the evidence responsibly, and reads like an architect wrote it.
    - Reject if it is missing important context, unsupported claims, or practical next steps.
    - Return JSON only with fields: approved, feedback, missing_points.
    """
