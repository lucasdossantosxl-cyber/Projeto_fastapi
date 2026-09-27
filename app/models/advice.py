"""Modelos das respostas e da validação do fornecedor."""

from datetime import UTC, datetime
from typing import Annotated, Self

from pydantic import BaseModel, Field, StringConstraints

AdviceText = Annotated[str, StringConstraints(strict=True, strip_whitespace=True, min_length=1)]


class AdviceSlip(BaseModel):
    advice: AdviceText


class ExternalAdviceResponse(BaseModel):
    slip: AdviceSlip


class AdviceResponse(BaseModel):
    original: str
    gritando: str
    sussurrando: str
    fetched_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @classmethod
    def from_raw_text(cls, text: str) -> Self:
        return cls(original=text, gritando=text.upper(), sussurrando=text.lower())


class HistoryResponse(BaseModel):
    last: int
    content: str
