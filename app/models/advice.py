"""Advice data models."""

from __future__ import annotations

from datetime import datetime
from typing import Self

from pydantic import BaseModel, Field


class AdviceResponse(BaseModel):
    """Schema returned by the /advice endpoint."""

    original: str = Field(..., description="Texto original do conselho")
    gritando: str = Field(..., description="Texto em MAIÚSCULAS")
    sussurrando: str = Field(..., description="Texto em minúsculas")
    fetched_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp UTC da consulta",
    )

    @classmethod
    def from_raw_text(cls, text: str) -> Self:
        """Factory: build from the raw advice string."""
        return cls(
            original=text,
            gritando=text.upper(),
            sussurrando=text.lower(),
        )


class HistoryEntry(BaseModel):
    """Single entry as stored in the history file."""

    original: str
    gritando: str
    sussurrando: str
    fetched_at: datetime

    def to_file_format(self) -> str:
        """Serialize to the legacy 3-line + separator format."""
        return (
            f"Original: {self.original}\n"
            f"Gritando: {self.gritando}\n"
            f"Sussurrando: {self.sussurrando}\n"
            f"{'-' * 30}\n"
        )
