from __future__ import annotations

import argparse
import json

from app.config import get_settings
from app.orchestrator import build_orchestrator


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the Planner + Researcher + Executor multi-agent workflow from the terminal."
    )
    parser.add_argument("goal", nargs="*", help="Goal for the agent system")
    parser.add_argument("--context", default="", help="Optional extra context")
    parser.add_argument("--json", action="store_true", help="Print the raw JSON response")
    args = parser.parse_args()

    goal = " ".join(args.goal).strip()
    if not goal:
        goal = input("Enter a goal for the agents: ").strip()
    if not goal:
        raise SystemExit("A goal is required.")

    orchestrator = build_orchestrator(get_settings())
    run = orchestrator.run(goal=goal, context=args.context)

    if args.json:
        print(json.dumps(run.model_dump(mode="json"), indent=2))
        return

    print("=" * 80)
    print(f"Run ID: {run.run_id}")
    print(f"Goal  : {run.goal}")
    print("=" * 80)
    print("Plan")
    print("-" * 80)
    for step in run.plan.steps:
        print(f"{step.step_id}. {step.title}")
        print(f"   Purpose      : {step.purpose}")
        print(f"   Search query : {step.research_query}")
        print(f"   Deliverable  : {step.deliverable}")
    print()
    print("Final Answer")
    print("-" * 80)
    print(run.final_answer)
    print()
    print("Metrics")
    print("-" * 80)
    print(json.dumps(run.metrics.model_dump(mode="json"), indent=2))


if __name__ == "__main__":
    main()
