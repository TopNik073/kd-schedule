from datetime import timedelta
from typing import TYPE_CHECKING
from fastapi import APIRouter, Depends, Query

from src.core.config import settings

from .dependencies import get_schedule_service

from .schemas import (
    SScheduleCreateRequest,
    SScheduleCreateResponse,
    SGetScheduleResponse,
    SGetNextTakingsResponse,
    SuccessResponseSScheduleCreateResponse,
    SuccessResponseSGetScheduleResponse,
    SuccessResponseListUUID,
    SuccessResponseListSGetNextTakingsResponse,
)
from uuid import UUID

if TYPE_CHECKING:
    from src.api.v1.schedule.service import ScheduleService

router = APIRouter(tags=["schedule"])


@router.post("/schedule")
async def create_schedule(
    create_schedule_dto: SScheduleCreateRequest,
    schedule_service: "ScheduleService" = Depends(get_schedule_service),
) -> SuccessResponseSScheduleCreateResponse:
    """
    Create a new schedule for a user. If user is not registered, it will be registered first.
    If end_time and duration are provided, it will use end_time.
    If only duration is provided, it will use current time + duration.
    If start_date is provided, it will use start_date.
    """
    schedule_id = await schedule_service.create_schedule(create_schedule_dto)
    return SuccessResponseSScheduleCreateResponse(data=SScheduleCreateResponse(id=schedule_id))


@router.get("/schedules")
async def get_schedules_ids(
    user_id: int = Query(..., gt=0, description="medicine policy number of user"),
    schedule_service: "ScheduleService" = Depends(get_schedule_service),
) -> SuccessResponseListUUID:
    """
    Get all schedules ids for a user.
    """
    schedule_ids = await schedule_service.get_schedules_ids_by_policy(user_id)
    return SuccessResponseListUUID(data=schedule_ids)


@router.get("/schedule")
async def get_schedule(
    user_id: int = Query(..., gt=0, description="medicine policy number of user"),
    schedule_id: UUID = Query(..., description="schedule unique UUID"),
    schedule_service: "ScheduleService" = Depends(get_schedule_service),
) -> SuccessResponseSGetScheduleResponse:
    """
    Get a schedule by id.
    """
    schedule = await schedule_service.get_schedule_by_id(user_id, schedule_id)
    return SuccessResponseSGetScheduleResponse(
        data=SGetScheduleResponse(
            medicine_name=schedule.medicine_name,
            frequency=schedule.frequency,
            start_date=schedule.start_date,
            end_date=schedule.end_date,
        )
    )


@router.get("/next_takings")
async def get_next_takings(
    user_id: int = Query(..., gt=0, description="medicine policy number of user"),
    next_takings: timedelta = Query(
        settings.NEXT_TAKING_TIMING, description="Optional manual next_taking interval"
    ),
    schedule_service: "ScheduleService" = Depends(get_schedule_service),
) -> SuccessResponseListSGetNextTakingsResponse:
    """
    Get next takings for a user.
    If next_takings is provided, it will use it instead of the default value from the config.
    """
    takings: list[SGetNextTakingsResponse] = await schedule_service.get_next_takings_with_model(
        user_id, next_takings
    )
    return SuccessResponseListSGetNextTakingsResponse(data=takings)
