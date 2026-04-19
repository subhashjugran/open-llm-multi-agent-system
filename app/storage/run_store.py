from __future__ import annotations

import json
from pathlib import Path

from app.schemas import AgentRun, RunSummary


class FileRunStore:
    """Persist agent runs as JSON files so they can be inspected later."""

    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _path_for(self, run_id: str) -> Path:
        return self.base_dir / f"{run_id}.json"

    def save(self, run: AgentRun) -> Path:
        path = self._path_for(run.run_id)
        payload = run.model_dump(mode="json")
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return path

    def load(self, run_id: str) -> AgentRun:
        path = self._path_for(run_id)
        if not path.exists():
            raise FileNotFoundError(f"Run '{run_id}' was not found")
        return AgentRun.model_validate_json(path.read_text(encoding="utf-8"))

    def list_runs(self, limit: int = 10) -> list[RunSummary]:
        paths = sorted(self.base_dir.glob("*.json"), reverse=True)[:limit]
        results: list[RunSummary] = []
        for path in paths:
            data = json.loads(path.read_text(encoding="utf-8"))
            metrics = data.get("metrics", {})
            results.append(
                RunSummary(
                    run_id=data.get("run_id", path.stem),
                    goal=data.get("goal", ""),
                    created_at=data.get("created_at", ""),
                    total_seconds=float(metrics.get("total_seconds", 0.0)),
                )
            )
        return results
