"""Busca um conselho, com persistência opcional."""

from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, Query
from starlette.concurrency import run_in_threadpool

from app.api.deps import get_http_client
from app.models.advice import AdviceResponse
from app.services.advice_service import fetch_advice
from app.services.history_service import save_to_history

router = APIRouter()


@router.get("", response_model=AdviceResponse)
async def get_advice(
    client: Annotated[httpx.AsyncClient, Depends(get_http_client)],
    save: Annotated[bool, Query(description="Persistir no histórico?")] = True,
) -> AdviceResponse:
    advice = await fetch_advice(client)
    if save:
        await run_in_threadpool(save_to_history, advice)
    return advice
