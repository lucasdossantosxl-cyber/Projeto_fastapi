"""GET /historico endpoint."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import history_last_param
from app.services.history_service import read_history

router = APIRouter()


@router.get("")
async def get_history(last: Annotated[int, Depends(history_last_param)]) -> dict[str, object]:
    """Retorna as últimas entradas do histórico."""
    content = read_history(last)
    return {"last": last, "content": content}
