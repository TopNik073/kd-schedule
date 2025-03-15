from typing import TYPE_CHECKING
from uuid import UUID
from datetime import datetime, timezone, UTC, timedelta, tzinfo

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.repositories import UserRepository, ScheduleRepository

from src.api.v1.schedule.schemas import (
    SScheduleCreateRequest,
    SUserBase,
    SScheduleCreate,
    SGetNextTakingsResponse,
)
from src.api.v1.schedule.utils import round_to_multiple, round_to_multiple_dt, find_next_takings
from src.core.logging import get_logger
from src.core.config import settings

from fastapi import HTTPException


if TYPE_CHECKING:
    from src.database.models.schedules import Schedules
    from src.database.models.users import Users

logger = get_logger(__name__)


class ScheduleService:
    def __init__(self, session: AsyncSession):
        self._schedule_repo = ScheduleRepository(session)
        self._user_repo = UserRepository(session)

    async def create_schedule(self, create_schedule_dto: SScheduleCreateRequest) -> UUID:
        try:
            user: "Users" | None = await self._user_repo.get_by_medical_policy(
                create_schedule_dto.medicine_policy
            )
            if user is None:
                user: "Users" = await self._user_repo.create(
                    SUserBase(
                        name=create_schedule_dto.name,
                        medicine_policy=create_schedule_dto.medicine_policy,
                    )
                )

            if not create_schedule_dto.start_date:
                start_date = round_to_multiple_dt(datetime.now(timezone.utc), 15)
            else:
                start_date = round_to_multiple_dt(create_schedule_dto.start_date, 15)

            start_date = start_date.replace(tzinfo=timezone.utc)

            if not (settings.MORNING_HOUR <= start_date.hour <= settings.EVENING_HOUR):
                raise ValueError(
                    f"Start time must be between {settings.MORNING_HOUR}:00 and {settings.EVENING_HOUR}:00"
                )

            end_date = create_schedule_dto.end_date

            if not end_date and create_schedule_dto.duration:
                end_date = start_date + create_schedule_dto.duration
                end_date = end_date.replace(tzinfo=timezone.utc)
                if not (settings.MORNING_HOUR <= end_date.hour <= settings.EVENING_HOUR):
                    raise ValueError(
                        f"End time (based on duration) must be between {settings.MORNING_HOUR}:00 and {settings.EVENING_HOUR}:00"
                    )
            elif end_date:
                end_date = end_date.replace(tzinfo=timezone.utc)
                if not (settings.MORNING_HOUR <= end_date.hour <= settings.EVENING_HOUR):
                    raise ValueError(
                        f"End time must be between {settings.MORNING_HOUR}:00 and {settings.EVENING_HOUR}:00"
                    )
            else:
                raise ValueError("Either end_date or duration must be provided")

            schedule: "Schedules" = await self._schedule_repo.create(
                SScheduleCreate(
                    medicine_name=create_schedule_dto.medicine_name,
                    frequency=round_to_multiple(create_schedule_dto.frequency, 15),
                    start_date=start_date,
                    end_date=end_date,
                    user_id=user.id,
                )
            )

            return schedule.id
        except ValueError as e:
            logger.warning(f"Validation error in create_schedule: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating schedule: {e}", exc_info=e)
            raise

    async def get_schedules_by_policy(self, medicine_policy: int) -> list["Schedules"]:
        users: list["Users"] | None = await self._user_repo.get_all_with_relations(
            ["schedules"], medicine_policy=medicine_policy
        )
        if len(users) != 1:
            raise HTTPException(404, f"User with medicine_policy {medicine_policy} not found")

        return users[0].schedules

    async def get_schedules_ids_by_policy(self, medicine_policy: int) -> list[UUID]:
        return [sch.id for sch in await self.get_schedules_by_policy(medicine_policy)]

    async def get_schedule_by_id(self, medicine_policy: int, schedule_id: UUID) -> "Schedules":
        user_schedules: list["Schedules"] = await self.get_schedules_by_policy(medicine_policy)
        schedule = [sch for sch in user_schedules if sch.id == schedule_id]
        if len(schedule) != 1:
            raise HTTPException(404, f"Schedule with id {schedule_id} not found")

        return schedule[0]

    async def get_next_takings(
        self,
        medicine_policy: int,
        next_takings_interval: timedelta = settings.NEXT_TAKING_TIMING,
    ) -> list[dict[str, "Schedules"]]:
        user_schedules: list["Schedules"] = await self.get_schedules_by_policy(medicine_policy)
        return find_next_takings(user_schedules, next_takings_interval)

    async def get_next_takings_with_model(
        self, medicine_policy: int, next_takings_interval: timedelta = settings.NEXT_TAKING_TIMING
    ) -> list[SGetNextTakingsResponse]:
        next_takings = await self.get_next_takings(medicine_policy, next_takings_interval)
        return [
            SGetNextTakingsResponse(
                medicine_name=taking["schedule"].medicine_name,
                frequency=taking["schedule"].frequency,
                start_date=taking["schedule"].start_date,
                end_date=taking["schedule"].end_date,
                next_taking_time=taking["next_taking_time"],
            )
            for taking in next_takings
        ]
