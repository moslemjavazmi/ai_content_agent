
import uuid

from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    String,
    Text,
    Uuid,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class ContentRecord(Base):
    __tablename__ = "content_records"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )

    platform: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    topic: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    content_data: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    image_data: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )

    image_prompt: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="pending_review",
        index=True,
    )

    review_notes: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
