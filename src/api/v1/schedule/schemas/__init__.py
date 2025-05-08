from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from src.api.v1.schedule.schemas.generated_schemas import (
    SGetNextTakingsResponse,
    SGetScheduleResponse,
    SScheduleCreateRequest,
    SScheduleCreateResponse,
    SuccessResponseListSGetNextTakingsResponse,
    SuccessResponseListUUID,
    SuccessResponseSGetScheduleResponse,
    SuccessResponseSScheduleCreateResponse,
)


class SScheduleCreate(BaseModel):
    medicine_name: str = Field(..., min_length=1)
    frequency: int = Field(..., gt=0)
    start_date: datetime
    end_date: datetime
    user_id: UUID


class SUserCreate(BaseModel):
    name: str | None = None
    medicine_policy: int = Field(..., gt=0)


__all__ = [
    "SGetNextTakingsResponse",
    "SGetScheduleResponse",
    "SScheduleCreate",
    "SScheduleCreateRequest",
    "SScheduleCreateResponse",
    "SUserCreate",
    "SuccessResponseListSGetNextTakingsResponse",
    "SuccessResponseListUUID",
    "SuccessResponseSGetScheduleResponse",
    "SuccessResponseSScheduleCreateResponse",
]
