"""Consulta e valida a API externa usando o cliente compartilhado."""

import httpx

from app.core.config import settings
from app.core.exceptions import ExternalAPIError
from app.models.advice import AdviceResponse, ExternalAdviceResponse


async def fetch_advice(client: httpx.AsyncClient) -> AdviceResponse:
    try:
        response = await client.get(str(settings.ADVICE_API_URL))
    except httpx.TimeoutException as exc:
        raise ExternalAPIError("Tempo limite da API externa excedido", status_code=504) from exc
    except httpx.RequestError as exc:
        raise ExternalAPIError("Não foi possível conectar à API externa") from exc

    if response.status_code != 200:
        raise ExternalAPIError("API externa retornou uma resposta sem sucesso")
    try:
        payload = ExternalAdviceResponse.model_validate_json(response.content)
    except ValueError as exc:
        raise ExternalAPIError("Resposta inesperada da API externa") from exc
    return AdviceResponse.from_raw_text(payload.slip.advice)
