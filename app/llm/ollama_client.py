from __future__ import annotations

from typing import Any

import requests

from app.schemas import JSONSchema
from app.utils import extract_json_object


class LLMError(RuntimeError):
    """Raised when the local LLM backend returns an error."""


class OllamaClient:
    """Small wrapper around Ollama's local chat API."""

    def __init__(self, base_url: str, timeout: int = 120, keep_alive: str = "5m") -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.keep_alive = keep_alive
        self.session = requests.Session()

    def _chat_payload(
        self,
        model: str,
        system_prompt: str,
        user_prompt: str,
        fmt: str | JSONSchema | None = None,
        temperature: float = 0.2,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
            "keep_alive": self.keep_alive,
            "options": {
                "temperature": temperature,
            },
        }
        if fmt is not None:
            payload["format"] = fmt
        return payload

    def chat(
        self,
        model: str,
        system_prompt: str,
        user_prompt: str,
        fmt: str | JSONSchema | None = None,
        temperature: float = 0.2,
    ) -> str:
        payload = self._chat_payload(
            model=model,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            fmt=fmt,
            temperature=temperature,
        )
        try:
            response = self.session.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()
            message = data.get("message", {})
            return str(message.get("content", "")).strip()
        except requests.RequestException as exc:
            raise LLMError(
                "Failed to call Ollama. Make sure Ollama is running and the model has been pulled."
            ) from exc

    def chat_json(
        self,
        model: str,
        system_prompt: str,
        user_prompt: str,
        schema: JSONSchema | None = None,
    ) -> dict[str, Any]:
        raw = self.chat(
            model=model,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            fmt=schema or "json",
            temperature=0.0,
        )
        data = extract_json_object(raw)
        if not isinstance(data, dict):
            raise LLMError("Expected a JSON object from the model")
        return data

    def list_models(self) -> list[str]:
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=15)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException:
            return []
        models = data.get("models", [])
        return [item.get("name", "") for item in models if item.get("name")]

    def is_available(self) -> bool:
        return bool(self.list_models())
