from uuid import UUID
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from app.database.database import Base, engine, get_db
from app.models.content import ContentRecord
from app.repositories.content_repository import content_repository
from app.schemas.content import (
    ContentRequest,
    ContentRecordResponse,
    RequestChanges,
)

from app.agent.tool_graph import run_business_agent
from typing import Literal
from app.agent.content_graph import create_content
from pathlib import Path
from fastapi.staticfiles import StaticFiles

Path("media/generated").mkdir(
    parents=True,
    exist_ok=True,
)

app = FastAPI(title="AI Content Agent")

app.mount(
    "/media",
    StaticFiles(directory="media"),
    name="media",
)
class AgentRequest(BaseModel):
    message: str = Field(min_length=1, max_length=3000)


class AgentResponse(BaseModel):
    answer: str


@app.get("/")
async def root():
    return {
        "message": "AI Content Agent is running"
    }


@app.post("/agent/run", response_model=AgentResponse)
def run_agent(request: AgentRequest):
    answer = run_business_agent(request.message)
    return AgentResponse(answer=answer)




class ContentRequest(BaseModel):
    topic: str = Field(min_length=3, max_length=200)
    platform: Literal["instagram", "linkedin"]



@app.post(
    "/content/generate",
    response_model=ContentRecordResponse,
)
def generate_and_save_content(
    request: ContentRequest,
    db: Session = Depends(get_db),
):
    package = create_content(
        topic=request.topic,
        platform=request.platform,
    )

    content_data = package["content"]
    image_data = dict(
        package.get("image", {})
    )

    if package.get("image_error"):
        image_data["error"] = package["image_error"]

    record = content_repository.create(
        db,
        platform=request.platform,
        topic=request.topic,
        content_data=content_data,
        image_data=image_data,
        image_prompt=package.get("image_prompt", ""),
    )

    return record


@app.get(
    "/content",
    response_model=list[ContentRecordResponse],
)
def list_content(
    status: str | None = Query(
        default=None,
        pattern="^(pending_review|approved|draft|published)$",
    ),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return content_repository.list_recent(
        db,
        status=status,
        limit=limit,
    )


@app.get(
    "/content/{content_id}",
    response_model=ContentRecordResponse,
)
def get_content(
    content_id: UUID,
    db: Session = Depends(get_db),
):
    record = content_repository.get_by_id(
        db,
        content_id,
    )

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Content not found",
        )

    return record


@app.post(
    "/content/{content_id}/approve",
    response_model=ContentRecordResponse,
)
def approve_content(
    content_id: UUID,
    db: Session = Depends(get_db),
):
    record = content_repository.get_by_id(
        db,
        content_id,
    )

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Content not found",
        )

    try:
        return content_repository.approve(db, record)
    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc


@app.post(
    "/content/{content_id}/request-changes",
    response_model=ContentRecordResponse,
)
def request_content_changes(
    content_id: UUID,
    request: RequestChanges,
    db: Session = Depends(get_db),
):
    record = content_repository.get_by_id(
        db,
        content_id,
    )

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Content not found",
        )

    try:
        return content_repository.request_changes(
            db,
            record,
            request.notes,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc
