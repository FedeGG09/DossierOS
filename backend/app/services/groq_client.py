import json
from typing import Any

from groq import Groq

from app.core.config import settings


class GroqClient:
    def __init__(self) -> None:
        self.client = Groq(api_key=settings.groq_api_key)
        self.model = settings.groq_model

    def chat_json(self, messages: list[dict[str, str]], temperature: float = 0.0, max_tokens: int = 3000) -> dict[str, Any]:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content or "{}"
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {"parse_error": True, "raw": content}
