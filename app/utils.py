from __future__ import annotations

import json
import re
from typing import Any


CODE_FENCE_JSON_RE = re.compile(r"```json\s*(.*?)```", re.IGNORECASE | re.DOTALL)
CODE_FENCE_RE = re.compile(r"```\s*(.*?)```", re.DOTALL)
WHITESPACE_RE = re.compile(r"\s+")


def normalize_whitespace(text: str) -> str:
    return WHITESPACE_RE.sub(" ", text or "").strip()


def safe_truncate(text: str, max_chars: int) -> str:
    text = normalize_whitespace(text)
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3].rstrip() + "..."


def _try_json(candidate: str) -> Any:
    return json.loads(candidate)


def _extract_balanced_json(text: str) -> str | None:
    starts = [index for index, char in enumerate(text) if char in "[{"]
    for start in starts:
        stack: list[str] = []
        in_string = False
        escape = False
        for index in range(start, len(text)):
            char = text[index]
            if in_string:
                if escape:
                    escape = False
                elif char == "\\":
                    escape = True
                elif char == '"':
                    in_string = False
                continue
            if char == '"':
                in_string = True
                continue
            if char in "[{":
                stack.append(char)
            elif char == "}" and stack and stack[-1] == "{":
                stack.pop()
            elif char == "]" and stack and stack[-1] == "[":
                stack.pop()
            if not stack:
                return text[start : index + 1]
    return None


def extract_json_object(text: str) -> Any:
    """Extract JSON from plain text or fenced Markdown code blocks."""

    if not text or not text.strip():
        raise ValueError("No content returned by the model")

    stripped = text.strip()
    try:
        return _try_json(stripped)
    except json.JSONDecodeError:
        pass

    for pattern in (CODE_FENCE_JSON_RE, CODE_FENCE_RE):
        matches = pattern.findall(text)
        for match in matches:
            candidate = match.strip()
            try:
                return _try_json(candidate)
            except json.JSONDecodeError:
                continue

    balanced = _extract_balanced_json(text)
    if balanced:
        return _try_json(balanced)

    raise ValueError("Could not find valid JSON in the model output")


def bullet_list(items: list[str]) -> str:
    if not items:
        return "- None"
    return "\n".join(f"- {item}" for item in items)
