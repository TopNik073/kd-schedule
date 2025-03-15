from src.database.models.schedules import Schedules
from src.repositories.base_repo import BaseRepository


class ScheduleRepository(BaseRepository[Schedules]):
    model: Schedules = Schedules
