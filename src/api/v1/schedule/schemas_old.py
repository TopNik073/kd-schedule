from datetime import datetime, timedelta
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, field_validator, ValidationInfo


# ---BASE SCHEMAS---
class SScheduleBase(BaseModel):
    medicine_name: str = Field(..., min_length=1)
    frequency: int = Field(..., gt=0)
    start_date: datetime | None = Field(None, description="timezone is always UTC")
    end_date: datetime | None = Field(None, description="timezone is always UTC")
    duration: timedelta | None = None

    @field_validator("start_date", mode="before")
    @classmethod
    def check_start_date_before_end_date(
        cls, value: datetime | None, info: ValidationInfo
    ) -> datetime | None:
        end_date = info.data.get("end_date")
        if value is None:
            return value
        if end_date is not None and value > end_date:
            raise ValueError("start_date must be before end_date")
        return value

    @field_validator("end_date", mode="before")
    @classmethod
    def check_end_date_and_duration(
        cls, value: datetime | None, info: ValidationInfo
    ) -> datetime | None:
        duration = info.data.get("duration")
        if value is None:
            return value
        if value.year == 1970:
            value = None
        if duration is not None and value is not None:
            raise ValueError("Only one of end_date or duration can be provided")
        return value


class SUserBase(BaseModel):
    name: str | None = None
    medicine_policy: int = Field(..., gt=0)


# ---CREATE SCHEDULE---
class SScheduleCreate(BaseModel):
    medicine_name: str = Field(..., min_length=1)
    frequency: int = Field(..., gt=0)
    start_date: datetime | None = None
    end_date: datetime | None = None
    user_id: UUID


class SScheduleCreateRequest(SScheduleBase, SUserBase):
    model_config = ConfigDict(from_attributes=True)


class SScheduleCreateResponse(BaseModel):
    id: UUID


# ---GET USER SCHEDULES---
class SGetSchedulesResponse(BaseModel):
    schedules: list[UUID]


# ---GET USER SCHEDULE---
class SGetScheduleResponse(SScheduleBase):
    model_config = ConfigDict(from_attributes=True)

    duration: timedelta | None = Field(None, exclude=True)


# ---GET NEXT TAKINGS---
class SGetNextTakingsResponse(SGetScheduleResponse):
    model_config = ConfigDict(from_attributes=True)

    next_taking_time: datetime
