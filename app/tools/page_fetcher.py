from __future__ import annotations

import requests
from bs4 import BeautifulSoup

from app.utils import normalize_whitespace, safe_truncate


class PageFetcher:
    """Fetch and compress HTML content for the research agent."""

    def __init__(self, timeout: int = 20, max_chars: int = 2200, user_agent: str | None = None) -> None:
        self.timeout = timeout
        self.max_chars = max_chars
        self.user_agent = user_agent or (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
        )
        self.session = requests.Session()

    def fetch_excerpt(self, url: str) -> str:
        headers = {"User-Agent": self.user_agent}
        try:
            response = self.session.get(url, timeout=self.timeout, headers=headers)
            response.raise_for_status()
            content_type = response.headers.get("content-type", "")
            if "html" not in content_type.lower():
                return ""
            soup = BeautifulSoup(response.text, "html.parser")
            for tag in soup(["script", "style", "noscript", "svg"]):
                tag.decompose()
            text = normalize_whitespace(soup.get_text(" "))
            return safe_truncate(text, self.max_chars)
        except requests.RequestException:
            return ""
