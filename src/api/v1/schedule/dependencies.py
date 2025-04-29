from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories import UserRepository, ScheduleRepository

from src.api.v1.schedule.service import ScheduleService
from src.database.connection import get_db


async def get_schedule_service(session: AsyncSession = Depends(get_db)) -> ScheduleService:
    user_repo: UserRepository = UserRepository(session)
    schedule_repo: ScheduleRepository = ScheduleRepository(session)
    return ScheduleService(user_repo=user_repo, schedule_repo=schedule_repo)
