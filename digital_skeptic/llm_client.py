from __future__ import annotations
from dataclasses import dataclass
from .config import Config
import google.generativeai as genai

@dataclass
class LLMClient:
    config: Config

    def _client(self):
        if not self.config.gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY is not set.")
        genai.configure(api_key=self.config.gemini_api_key)

    def complete(self, system: str, user: str) -> str:
        """
        For Gemini, we'll merge `system` and `user` into one prompt since
        system messages aren't a separate role in their API.
        """
        self._client()
        model = genai.GenerativeModel(self.config.gemini_model)
        prompt = f"System instructions:\n{system}\n\nUser input:\n{user}"
        resp = model.generate_content(prompt)
        return resp.text.strip()
