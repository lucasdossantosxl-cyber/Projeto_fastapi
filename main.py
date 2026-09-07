from __future__ import annotations

import os
from typing import Any

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

HISTORICO_PATH = os.path.join(os.path.dirname(__file__), "historico_conselhos.txt")
ADVICE_URL = "https://api.adviceslip.com/advice"

app = FastAPI(title="Gerenciador de Conselhos API")


class AdviceResponse(BaseModel):
    original: str
    gritando: str
    sussurrando: str


def _fetch_advice() -> str:
    try:
        resp = requests.get(ADVICE_URL, timeout=5)
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Erro de conexão: {e}")

    if resp.status_code != 200:
        raise HTTPException(
            status_code=resp.status_code,
            detail="Erro ao consultar API externa",
        )

    try:
        data: Any = resp.json()
        return str(data["slip"]["advice"])
    except Exception:
        raise HTTPException(status_code=502, detail="Resposta inesperada da API externa")


def _save_history(entry: AdviceResponse) -> None:
    # Mantém compatível com o formato do seu script antigo (3 linhas por conselho)
    with open(HISTORICO_PATH, "a", encoding="utf-8") as f:
        f.write(f"Original: {entry.original}\n")
        f.write(f"Gritando: {entry.gritando}\n")
        f.write(f"Sussurrando: {entry.sussurrando}\n")
        f.write("-" * 30 + "\n")


@app.get("/advice", response_model=AdviceResponse)
def get_advice(save: bool = True) -> AdviceResponse:
    text = _fetch_advice()
    payload = AdviceResponse(
        original=text,
        gritando=text.upper(),
        sussurrando=text.lower(),
    )

    if save:
        _save_history(payload)

    return payload


@app.get("/historico")
def get_history(last: int = 15):
    if not os.path.exists(HISTORICO_PATH):
        return {"last": last, "content": "(sem histórico ainda)"}

    with open(HISTORICO_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    snippet = "".join(lines[-max(0, last) :])
    return {"last": last, "content": snippet}


