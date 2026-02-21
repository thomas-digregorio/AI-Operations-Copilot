from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class Citation(BaseModel):
    source: str
    snippet: str
    score: float | None = None


class WarningItem(BaseModel):
    code: str
    message: str


class APIStatus(BaseModel):
    status: str = "ok"
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class KeyValueMetric(BaseModel):
    name: str
    value: float | int | str | bool | dict[str, Any]
