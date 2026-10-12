
from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ContentRequest(BaseModel):
    topic: str = Field(min_length=3, max_length=200)
    platform: Literal["instagram", "linkedin"]


class ContentRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    platform: str
    topic: str

    content_data: dict[str, Any]
    image_data: dict[str, Any]
    image_prompt: str

    status: str
    review_notes: str

    created_at: datetime
    updated_at: datetime
    reviewed_at: datetime | None


class RequestChanges(BaseModel):
    notes: str = Field(min_length=3, max_length=2000)
