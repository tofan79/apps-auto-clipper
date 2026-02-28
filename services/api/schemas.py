from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    status: str
    service: str


class JobCreateRequest(BaseModel):
    source_url: str = Field(min_length=1)
    source_type: Literal["youtube", "local"]
    user_id: str | None = None


class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str | None
    source_url: str
    source_type: str
    status: str
    progress_pct: int
    current_stage: str | None
    error_msg: str | None
    checkpoint_path: str | None
    created_at: datetime
    updated_at: datetime


class JobStatusResponse(BaseModel):
    id: str
    status: str
    progress_pct: int
    current_stage: str | None
    error_msg: str | None


class JobQueueActionResponse(BaseModel):
    id: str
    accepted: bool


class JobReorderRequest(BaseModel):
    index: int = Field(ge=0)


class ClipResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    job_id: str
    file_path: str
    thumbnail_path: str | None
    mode: str
    viral_score: int
    duration_sec: int
    created_at: datetime


class ClipPreviewResponse(BaseModel):
    clip_id: str
    file_path: str
    thumbnail_path: str | None
    metadata: dict[str, Any]


class SettingsResponse(BaseModel):
    values: dict[str, Any]


class SettingsUpdateRequest(BaseModel):
    values: dict[str, Any] = Field(default_factory=dict)


class ApiKeyUpdateRequest(BaseModel):
    provider: Literal["openrouter", "openai"]
    api_key: str = Field(min_length=1)


class MessageResponse(BaseModel):
    message: str


class ProgressEvent(BaseModel):
    job_id: str
    status: str
    progress_pct: int = Field(ge=0, le=100)
    current_stage: str | None = None
    message: str | None = None
    timestamp: str
