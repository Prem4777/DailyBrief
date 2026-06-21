"""
services/gemini_service.py — Wrapper around the Google Gen AI SDK.

Supports both old (AIza) and new (AQ) API key formats via google-genai SDK.
Retries with exponential backoff; honours the retryDelay hint on 429s.
"""

from __future__ import annotations

import asyncio
import logging
import re

from config import settings

logger = logging.getLogger(__name__)

_DEFAULT_MODEL = "gemini-1.5-flash"
_MAX_RETRIES = 3
_INITIAL_BACKOFF = 2.0
_MAX_BACKOFF = 64.0


def _extract_retry_delay(exc: Exception) -> float | None:
    """Pull the suggested retryDelay (seconds) out of a 429 error message."""
    try:
        text = str(exc)
        # Matches "'retryDelay': '52s'" or "retryDelay: 52.9s"
        m = re.search(r"retryDelay['\"\s:]+(\d+(?:\.\d+)?)", text)
        if m:
            return float(m.group(1)) + 1.0   # add 1s buffer
    except Exception:
        pass
    return None


class GeminiService:
    def __init__(self, model_name: str = _DEFAULT_MODEL) -> None:
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is not set in .env")

        self._model_name = model_name
        self._api_key = settings.gemini_api_key

        # Try new google-genai SDK first, fall back to old google-generativeai
        self._use_new_sdk = False
        try:
            from google import genai
            self._client = genai.Client(api_key=self._api_key)
            self._use_new_sdk = True
            logger.info("Using google-genai SDK")
        except Exception:
            import google.generativeai as genai_old
            genai_old.configure(api_key=self._api_key)
            self._model = genai_old.GenerativeModel(model_name)
            logger.info("Using google-generativeai SDK")

    async def generate(self, prompt: str, response_schema: type | None = None) -> str:
        backoff = _INITIAL_BACKOFF
        last_exc = None

        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                if self._use_new_sdk:
                    return await self._generate_new_sdk(prompt)
                else:
                    return await self._generate_old_sdk(prompt)
            except Exception as exc:
                last_exc = exc
                logger.warning("Gemini attempt %d/%d failed: %s", attempt, _MAX_RETRIES, exc)
                if attempt < _MAX_RETRIES:
                    # Honour the server's retryDelay hint if present (429s),
                    # otherwise fall back to exponential backoff.
                    delay = _extract_retry_delay(exc) or backoff
                    delay = min(delay, _MAX_BACKOFF)
                    logger.info("Gemini backing off for %.1fs before retry %d", delay, attempt + 1)
                    await asyncio.sleep(delay)
                    backoff = min(backoff * 2, _MAX_BACKOFF)

        raise RuntimeError(f"Gemini failed after {_MAX_RETRIES} attempts: {last_exc}")

    async def _generate_new_sdk(self, prompt: str) -> str:
        from google import genai
        response = await asyncio.to_thread(
            self._client.models.generate_content,
            model=self._model_name,
            contents=prompt,
        )
        return response.text

    async def _generate_old_sdk(self, prompt: str) -> str:
        response = await asyncio.to_thread(
            self._model.generate_content,
            prompt,
        )
        return response.text
