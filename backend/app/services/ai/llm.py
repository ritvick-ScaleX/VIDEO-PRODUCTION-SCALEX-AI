"""Text generation client — OpenAI GPT with graceful mock fallback.

The product stays usable without an API key: when ``OPENAI_API_KEY`` is unset —
or a live call fails — the caller-supplied ``mock`` payload is returned instead.
Mocks live next to each service so they always match the expected shape.

Live calls use Chat Completions with Structured Outputs (``response_format`` =
``json_schema`` strict) so responses are guaranteed-parseable JSON. The
``thinking`` / ``effort`` kwargs are accepted for call-site compatibility and
ignored by this provider.
"""
from __future__ import annotations

import json
from typing import Any, Callable

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

MockLike = dict | list | Callable[[], Any]


def _resolve_mock(mock: MockLike) -> Any:
    return mock() if callable(mock) else mock


def _is_reasoning_model(model: str) -> bool:
    """GPT-5-class + o-series accept a `reasoning_effort` param; gpt-4o etc. don't."""
    m = (model or "").lower()
    return m.startswith("gpt-5") or m.startswith(("o1", "o3", "o4"))


class LLMClient:
    """Thin async wrapper over the OpenAI SDK."""

    def __init__(self) -> None:
        self._client = None
        if settings.text_ai_enabled:
            try:
                from openai import AsyncOpenAI

                self._client = AsyncOpenAI(api_key=settings.openai_api_key)
                logger.info("Text AI: OpenAI live (model=%s)", settings.openai_model)
            except Exception as exc:  # pragma: no cover - defensive
                logger.warning("Text AI: failed to init OpenAI (%s) — mock mode", exc)
                self._client = None
        else:
            logger.info("Text AI: mock mode (no OPENAI_API_KEY)")

    @property
    def enabled(self) -> bool:
        return self._client is not None

    @property
    def mode(self) -> str:
        return "live" if self.enabled else "mock"

    @property
    def provider(self) -> str:
        return "openai"

    async def _create(self, **kwargs):
        """Chat-completions call that adds reasoning_effort for reasoning models, and
        transparently retries WITHOUT it if the model/SDK rejects the param — so a
        model swap can never silently drop us into mock mode over one kwarg."""
        model = kwargs.get("model", "")
        if _is_reasoning_model(model):
            try:
                return await self._client.chat.completions.create(
                    reasoning_effort=settings.openai_reasoning_effort, **kwargs
                )
            except TypeError:
                pass  # SDK too old for the kwarg → fall through
            except Exception as exc:
                if "reasoning" in str(exc).lower():
                    pass  # model rejected the param → fall through
                else:
                    raise
        return await self._client.chat.completions.create(**kwargs)

    async def generate_structured(
        self,
        *,
        system: str,
        prompt: str,
        schema: dict[str, Any],
        mock: MockLike,
        model: str | None = None,
        max_tokens: int | None = None,
        thinking: bool = False,  # accepted for compatibility; unused
        effort: str = "high",  # accepted for compatibility; unused
    ) -> Any:
        """Return validated JSON matching ``schema``, or the mock payload."""
        if not self.enabled:
            return _resolve_mock(mock)
        try:
            resp = await self._create(
                model=model or settings.openai_model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "auralis_result",
                        "schema": schema,
                        "strict": True,
                    },
                },
                max_completion_tokens=max_tokens or settings.ai_max_tokens,
            )
            content = resp.choices[0].message.content or ""
            return json.loads(content)
        except Exception as exc:
            logger.warning("OpenAI generate_structured failed (%s) — mock", exc)
            return _resolve_mock(mock)

    async def generate_text(
        self,
        *,
        system: str,
        prompt: str,
        mock: str | Callable[[], str],
        model: str | None = None,
        max_tokens: int | None = None,
    ) -> str:
        if not self.enabled:
            return mock() if callable(mock) else mock
        try:
            resp = await self._create(
                model=model or settings.openai_model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
                max_completion_tokens=max_tokens or settings.ai_max_tokens,
            )
            return resp.choices[0].message.content or ""
        except Exception as exc:
            logger.warning("OpenAI generate_text failed (%s) — mock", exc)
            return mock() if callable(mock) else mock


llm = LLMClient()
