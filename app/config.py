from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env", override=False)


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _path_from_env(name: str, default: str) -> Path:
    raw = Path(os.getenv(name, default))
    return raw if raw.is_absolute() else BASE_DIR / raw


@dataclass(slots=True)
class Settings:
    """Runtime configuration for the multi-agent system."""

    base_dir: Path = field(default_factory=lambda: BASE_DIR)
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    planner_model: str = os.getenv("PLANNER_MODEL", "llama3.2:3b")
    researcher_model: str = os.getenv("RESEARCHER_MODEL", os.getenv("PLANNER_MODEL", "llama3.2:3b"))
    executor_model: str = os.getenv("EXECUTOR_MODEL", os.getenv("PLANNER_MODEL", "llama3.2:3b"))
    critic_model: str = os.getenv(
        "CRITIC_MODEL",
        os.getenv("EXECUTOR_MODEL", os.getenv("PLANNER_MODEL", "llama3.2:3b")),
    )
    max_steps: int = int(os.getenv("MAX_STEPS", "4"))
    max_search_results: int = int(os.getenv("MAX_SEARCH_RESULTS", "5"))
    max_pages_per_step: int = int(os.getenv("MAX_PAGES_PER_STEP", "2"))
    max_extract_chars: int = int(os.getenv("MAX_EXTRACT_CHARS", "2200"))
    request_timeout: int = int(os.getenv("REQUEST_TIMEOUT", "120"))
    enable_critic: bool = _as_bool(os.getenv("ENABLE_CRITIC"), True)
    fetch_url_content: bool = _as_bool(os.getenv("FETCH_URL_CONTENT"), True)
    output_dir: Path = field(default_factory=lambda: _path_from_env("OUTPUT_DIR", "data/runs"))
    keep_alive: str = os.getenv("OLLAMA_KEEP_ALIVE", "5m")
    web_region: str = os.getenv("WEB_REGION", "us-en")
    user_agent: str = os.getenv(
        "USER_AGENT",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    )

    def __post_init__(self) -> None:
        self.ollama_base_url = self.ollama_base_url.rstrip("/")
        self.output_dir.mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
