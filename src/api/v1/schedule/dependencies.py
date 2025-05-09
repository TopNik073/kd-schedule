from typing import Annotated

from fastapi import Depends

from src.api.v1.schedule.service import ScheduleService
from src.database.connection import DB_DEPENDENCY
from src.repositories import ScheduleRepository, UserRepository


async def get_schedule_service(session: DB_DEPENDENCY) -> ScheduleService:
    user_repo: UserRepository = UserRepository(session)
    schedule_repo: ScheduleRepository = ScheduleRepository(session)
    return ScheduleService(user_repo=user_repo, schedule_repo=schedule_repo)


SCHEDULE_SERVICE_DEPENDENCY = Annotated[ScheduleService, Depends(get_schedule_service)]
