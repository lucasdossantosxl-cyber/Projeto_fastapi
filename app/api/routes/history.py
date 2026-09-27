"""A rota síncrona é executada pelo FastAPI em uma thread."""

from typing import Annotated

from fastapi import APIRouter, Query

from app.models.advice import HistoryResponse
from app.services.history_service import read_history

router = APIRouter()


@router.get("", response_model=HistoryResponse)
def get_history(
    last: Annotated[int, Query(ge=1, le=100, description="Número de entradas recentes")] = 15,
) -> HistoryResponse:
    return HistoryResponse(last=last, content=read_history(last))
