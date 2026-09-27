"""Dependências compartilhadas pelas rotas."""

from typing import cast

import httpx
from fastapi import Request


def get_http_client(request: Request) -> httpx.AsyncClient:
    return cast(httpx.AsyncClient, request.app.state.http_client)
