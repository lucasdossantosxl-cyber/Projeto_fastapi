"""Main API router aggregating all sub-routers."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.routes import advice, history

api_router = APIRouter()
api_router.include_router(advice.router, prefix="/advice", tags=["advice"])
api_router.include_router(history.router, prefix="/historico", tags=["history"])
