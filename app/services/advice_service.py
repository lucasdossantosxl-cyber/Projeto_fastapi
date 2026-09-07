"""Service layer: fetch advice from external API."""

from __future__ import annotations

from typing import Any

import httpx

from app.core.config import settings
from app.core.exceptions import ExternalAPIError
from app.core.logging import get_logger
from app.models.advice import AdviceResponse

logger = get_logger(__name__)


async def fetch_advice() -> AdviceResponse:
    """Fetch a random advice from the external API asynchronously.

    Raises:
        ExternalAPIError: on network failure, non-2xx status, or malformed JSON.
    """
    logger.info("Fetching advice from external API", extra={"url": settings.ADVICE_API_URL})

    async with httpx.AsyncClient(timeout=settings.ADVICE_API_TIMEOUT) as client:
        try:
            response = await client.get(settings.ADVICE_API_URL)
        except httpx.RequestError as exc:
            logger.exception("Network error while fetching advice")
            raise ExternalAPIError(f"Erro de conexão: {exc}", status_code=502) from exc

    if response.status_code != 200:
        logger.warning(
            "External API returned non-200 status",
            extra={"status_code": response.status_code, "body": response.text[:200]},
        )
        raise ExternalAPIError(
            f"API externa retornou status {response.status_code}",
            status_code=response.status_code,
        )

    try:
        data: Any = response.json()
        raw_text: str = data["slip"]["advice"]
    except (KeyError, TypeError, ValueError) as exc:
        logger.exception("Unexpected response structure from external API")
        raise ExternalAPIError("Resposta inesperada da API externa", status_code=502) from exc

    logger.info("Advice fetched successfully", extra={"advice_preview": raw_text[:50]})
    return AdviceResponse.from_raw_text(raw_text)
