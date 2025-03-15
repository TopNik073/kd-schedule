from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.schedule.service import ScheduleService
from src.database.connection import get_db


async def get_schedule_service(session: AsyncSession = Depends(get_db)) -> ScheduleService:
    return ScheduleService(session)
