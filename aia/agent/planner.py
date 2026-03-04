from __future__ import annotations

import json
import os
from typing import Any, Dict, List

import requests


class GeminiPlanner:
    def __init__(self, api_key: str | None = None, model: str = "gemini-1.5-flash") -> None:
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY is not configured.")

    def build_plan(self, user_command: str) -> List[Dict[str, Any]]:
        system_prompt = (
            "You are an AI desktop planning engine. Convert user intent to strict JSON array of steps. "
            "Each object MUST include keys: step_id(int), description(string), action_type(string), "
            "parameters(object), is_critical(boolean). Never return markdown or comments."
        )

        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
            f"?key={self.api_key}"
        )
        body = {
            "system_instruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"parts": [{"text": user_command}]}],
            "generationConfig": {"response_mime_type": "application/json"},
        }

        response = requests.post(url, json=body, timeout=30)
        response.raise_for_status()
        data = response.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        parsed = json.loads(text)
        if not isinstance(parsed, list):
            raise ValueError("Planner response must be a JSON list")
        return parsed
