"""FastAPI dependencies (injectables)."""

from __future__ import annotations

from typing import Annotated

from fastapi import Query


async def history_last_param(
    last: Annotated[int, Query(ge=1, le=100, description="Número de entradas recentes")] = 15,
) -> int:
    """Validated 'last' query parameter for /historico."""
    return last
