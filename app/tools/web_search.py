from __future__ import annotations

from typing import Iterable

from app.schemas import WebEvidence


class WebSearchTool:
    """Simple no-key web search powered by DDGS."""

    def __init__(self, max_results: int = 5, region: str = "us-en") -> None:
        self.max_results = max_results
        self.region = region

    def _import_ddgs(self):
        try:
            from ddgs import DDGS
        except ImportError as exc:
            raise RuntimeError(
                "The ddgs package is not installed. Run `pip install -r requirements.txt` first."
            ) from exc
        return DDGS

    def search(self, query: str) -> list[WebEvidence]:
        DDGS = self._import_ddgs()
        results = DDGS(timeout=10).text(
            query=query,
            region=self.region,
            safesearch="moderate",
            max_results=self.max_results,
            backend="auto",
        )
        items = list(results or [])
        deduped: list[WebEvidence] = []
        seen: set[str] = set()
        rank = 1
        for item in items:
            url = str(item.get("href", "")).strip()
            if not url or url in seen:
                continue
            seen.add(url)
            deduped.append(
                WebEvidence(
                    rank=rank,
                    title=str(item.get("title", "Untitled result")).strip(),
                    url=url,
                    snippet=str(item.get("body", "")).strip(),
                )
            )
            rank += 1
        return deduped
