from sqlalchemy import select

from src.database.models.users import Users
from src.repositories.base_repo import BaseRepository


class UserRepository(BaseRepository[Users]):
    model: Users = Users

    async def get_by_medical_policy(self, medical_policy: int) -> Users | None:
        query = select(self.model).where(self.model.medicine_policy == medical_policy)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()
