from datetime import timedelta
from typing import TYPE_CHECKING
from fastapi import APIRouter, Depends, HTTPException, Query

from src.core.logging import get_logger
from src.core.config import settings

from .dependencies import get_schedule_service

from .schemas import (
    SScheduleCreateRequest,
    SScheduleCreateResponse,
    SGetScheduleResponse,
    SGetNextTakingsResponse,
)
from uuid import UUID
from src.api.v1.response_schemas import SuccessResponseSchema


if TYPE_CHECKING:
    from src.api.v1.schedule.service import ScheduleService

logger = get_logger(__name__)

router = APIRouter(tags=["schedule"])


@router.post("/schedule")
async def create_schedule(
    create_schedule_dto: SScheduleCreateRequest,
    schedule_service: "ScheduleService" = Depends(get_schedule_service),
) -> SuccessResponseSchema[SScheduleCreateResponse]:
    """
    Create a new schedule for a user. If user is not registered, it will be registered first.
    If end_time and duration are provided, it will use end_time.
    If only duration is provided, it will use current time + duration.
    If start_date is provided, it will use start_date.
    """
    try:
        schedule_id = await schedule_service.create_schedule(create_schedule_dto)
        return SuccessResponseSchema(data=SScheduleCreateResponse(id=schedule_id))
    except ValueError as e:
        logger.exception(f"Validation error", exc_info=e)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"Error creating schedule", exc_info=e)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/schedules")
async def get_schedules_ids(
    user_id: int = Query(..., gt=0, description="medicine policy number of user"),
    schedule_service: "ScheduleService" = Depends(get_schedule_service),
) -> SuccessResponseSchema[list[UUID]]:
    """
    Get all schedules ids for a user.
    """
    try:
        schedule_ids = await schedule_service.get_schedules_ids_by_policy(user_id)
        return SuccessResponseSchema(data=schedule_ids)
    except ValueError as e:
        logger.exception(f"Validation error", exc_info=e)
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error getting schedules", exc_info=e)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/schedule")
async def get_schedule(
    user_id: int = Query(..., gt=0, description="medicine policy number of user"),
    schedule_id: UUID = Query(..., description="schedule unique UUID"),
    schedule_service: "ScheduleService" = Depends(get_schedule_service),
) -> SuccessResponseSchema[SGetScheduleResponse]:
    """
    Get a schedule by id.
    """
    try:
        schedule = await schedule_service.get_schedule_by_id(user_id, schedule_id)
        return SuccessResponseSchema(data=SGetScheduleResponse.model_validate(schedule))
    except ValueError as e:
        logger.exception(f"Validation error", exc_info=e)
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error getting schedule by id", exc_info=e)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/next_takings")
async def get_next_takings(
    user_id: int = Query(..., gt=0, description="medicine policy number of user"),
    next_takings: timedelta = Query(
        settings.NEXT_TAKING_TIMING, description="Optional manual next_taking interval"
    ),
    schedule_service: "ScheduleService" = Depends(get_schedule_service),
) -> SuccessResponseSchema[list[SGetNextTakingsResponse]]:
    """
    Get next takings for a user.
    If next_takings is provided, it will use it instead of the default value from the config.
    """
    try:
        takings: list[SGetNextTakingsResponse] = await schedule_service.get_next_takings_with_model(
            user_id, next_takings
        )
        return SuccessResponseSchema(data=takings)
    except ValueError as e:
        logger.exception(f"Validation error", exc_info=e)
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error getting taking schedule", exc_info=e)
        raise HTTPException(status_code=500, detail="Internal server error")
