
import uuid

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.content import ContentRecord


class ContentRepository:

    def create(
        self,
        db: Session,
        *,
        platform: str,
        topic: str,
        content_data: dict,
        image_data: dict,
        image_prompt: str,
    ) -> ContentRecord:

        record = ContentRecord(
            platform=platform,
            topic=topic,
            content_data=content_data,
            image_data=image_data,
            image_prompt=image_prompt,
            status="pending_review",
        )

        db.add(record)
        db.commit()
        db.refresh(record)

        return record

    def get_by_id(
        self,
        db: Session,
        content_id: uuid.UUID,
    ) -> ContentRecord | None:

        return db.get(ContentRecord, content_id)

    def list_recent(
        self,
        db: Session,
        *,
        status: str | None = None,
        limit: int = 20,
    ) -> list[ContentRecord]:

        query = select(ContentRecord).order_by(
            ContentRecord.created_at.desc()
        )

        if status:
            query = query.where(
                ContentRecord.status == status
            )

        query = query.limit(limit)

        return list(db.scalars(query).all())

    def approve(
        self,
        db: Session,
        record: ContentRecord,
    ) -> ContentRecord:

        if record.status != "pending_review":
            raise ValueError(
                "Only pending content can be approved."
            )

        record.status = "approved"
        record.reviewed_at = datetime.now(timezone.utc)
        record.review_notes = ""

        db.commit()
        db.refresh(record)

        return record

    def request_changes(
        self,
        db: Session,
        record: ContentRecord,
        notes: str,
    ) -> ContentRecord:

        if record.status != "pending_review":
            raise ValueError(
                "Only pending content can be sent for changes."
            )

        record.status = "draft"
        record.review_notes = notes
        record.reviewed_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(record)

        return record


content_repository = ContentRepository()
