"""GET /advice endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Query

from app.core.logging import get_logger
from app.models.advice import AdviceResponse
from app.services.advice_service import fetch_advice
from app.services.history_service import save_to_history

logger = get_logger(__name__)
router = APIRouter()


@router.get("", response_model=AdviceResponse)
async def get_advice(save: bool = Query(True, description="Persistir no histórico?")) -> AdviceResponse:
    """Busca um conselho aleatório, transforma e opcionalmente salva."""
    advice = await fetch_advice()

    if save:
        save_to_history(advice)
        logger.info("Advice saved to history", extra={"save": True})
    else:
        logger.info("Advice fetched without saving", extra={"save": False})

    return advice
