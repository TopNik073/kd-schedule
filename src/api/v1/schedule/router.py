from datetime import timedelta
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query

from src.api.v1.schedule.dependencies import SCHEDULE_SERVICE_DEPENDENCY
from src.api.v1.schedule.schemas import (
    SGetNextTakingsResponse,
    SGetScheduleResponse,
    SScheduleCreateRequest,
    SScheduleCreateResponse,
    SuccessResponseListSGetNextTakingsResponse,
    SuccessResponseListUUID,
    SuccessResponseSGetScheduleResponse,
    SuccessResponseSScheduleCreateResponse,
)

router = APIRouter(tags=["schedule"])

USER_ID_QUERY = Annotated[int, Query(..., gt=0, description="medicine policy number of user")]
SCHEDULE_ID_QUERY = Annotated[UUID, Query(..., description="schedule unique UUID")]
NEXT_TAKINGS_QUERY = Annotated[
    timedelta, Query(..., description="Optional manual next_taking interval")
]


@router.post("/schedule")
async def create_schedule(
    schedule_service: SCHEDULE_SERVICE_DEPENDENCY,
    create_schedule_dto: SScheduleCreateRequest,
) -> SuccessResponseSScheduleCreateResponse:
    """
    Create a new schedule for a user. If user is not registered, it will be registered first.
    If end_time and duration are provided, it will use end_time.
    If only duration is provided, it will use current time + duration.
    If start_date is provided, it will use start_date.
    """
    schedule_id = await schedule_service.create_schedule(create_schedule_dto)
    return SuccessResponseSScheduleCreateResponse(
        data=SScheduleCreateResponse(schedule_id=schedule_id)
    )


@router.get("/schedules")
async def get_schedules_ids(
    schedule_service: SCHEDULE_SERVICE_DEPENDENCY,
    user_id: USER_ID_QUERY,
) -> SuccessResponseListUUID:
    """
    Get all schedules ids for a user.
    """
    schedule_ids = await schedule_service.get_schedules_ids_by_policy(user_id)
    return SuccessResponseListUUID(data=schedule_ids)


@router.get("/schedule")
async def get_schedule(
    schedule_service: SCHEDULE_SERVICE_DEPENDENCY,
    user_id: USER_ID_QUERY,
    schedule_id: SCHEDULE_ID_QUERY,
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
            schedule_id=schedule.id,
        )
    )


@router.get("/next_takings")
async def get_next_takings(
    schedule_service: SCHEDULE_SERVICE_DEPENDENCY,
    user_id: USER_ID_QUERY,
    next_takings: NEXT_TAKINGS_QUERY | None = None,
) -> SuccessResponseListSGetNextTakingsResponse:
    """
    Get next takings for a user.
    If next_takings is provided, it will use it instead of the default value from the config.
    """
    takings: list[SGetNextTakingsResponse] = await schedule_service.get_next_takings_with_model(
        user_id, next_takings
    )
    return SuccessResponseListSGetNextTakingsResponse(data=takings)
