from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel as PydanticBaseModel
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.database.models.base_model import BaseModel

MODEL_TYPE = TypeVar("MODEL_TYPE", bound=BaseModel)
PYDANTIC_TYPE = TypeVar("PYDANTIC_TYPE", bound=PydanticBaseModel)


class IBaseRepository(Generic[MODEL_TYPE], ABC):
    """
    Base repository interface
    """

    @abstractmethod
    async def create(self, data: dict[str, Any] | PYDANTIC_TYPE) -> MODEL_TYPE:
        """
        Create a new record in the repository.

        Args:
            data: Data for creating a record

        Returns:
            Created record
        """
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, id: UUID) -> MODEL_TYPE | None:
        """
        Get a record by id.

        Args:
            id: Record id

        Returns:
            Record or None if record not found
        """
        raise NotImplementedError

    @abstractmethod
    async def get_by_field(self, field: str, value: Any) -> MODEL_TYPE | None:
        """
        Get a record by a specific field.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_all(self, **filters: dict[str, Any]) -> list[MODEL_TYPE]:
        """
        Get all records that match the filters.

        Args:
            filters: Filters for the query

        Returns:
            List of records
        """
        raise NotImplementedError

    @abstractmethod
    async def get_by_id_with_relations(
        self, id: UUID, relations: list[str] | None = None
    ) -> MODEL_TYPE:
        """
        Get a record by id with relations.

        Args:
            id: Record id
            relations: Relations to load

        Returns:
            Record with relations
        """
        raise NotImplementedError

    @abstractmethod
    async def get_all_with_relations(
        self, relations: list[str] | None = None, **filters: dict[str, Any]
    ) -> list[MODEL_TYPE]:
        """
        Get all records with relations.

        Args:
            relations: Relations to load
            filters: Filters for the query

        Returns:
            List of records with relations
        """
        raise NotImplementedError

    @abstractmethod
    async def update(self, id: UUID, data: dict[str, Any]) -> MODEL_TYPE | None:
        """
        Update a record by id.

        Args:
            id: Record id
            data: Data for updating

        Returns:
            Updated record or None if record not found
        """
        raise NotImplementedError

    @abstractmethod
    async def delete(self, id: UUID) -> bool:
        """
        Delete a record by id.

        Args:
            id: Record id

        Returns:
            True if the record was deleted, otherwise False
        """
        raise NotImplementedError


class BaseRepository(IBaseRepository[MODEL_TYPE]):
    model: type[MODEL_TYPE]

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, data: dict[str, Any] | PYDANTIC_TYPE) -> MODEL_TYPE:
        if isinstance(data, PydanticBaseModel):
            data = data.model_dump()

        obj = self.model(**data)

        self._session.add(obj)
        await self._session.commit()
        await self._session.refresh(obj)

        return obj

    async def get_by_id(self, id: UUID) -> MODEL_TYPE:
        query = select(self.model).where(self.model.id == id)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_field(self, field: str, value: Any) -> MODEL_TYPE | None:
        query = select(self.model).where(getattr(self.model, field) == value)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(self, **filters: dict[str, Any]) -> list[MODEL_TYPE]:
        query = select(self.model)
        if filters:
            for field, value in filters.items():
                query = query.where(getattr(self.model, field) == value)
        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_by_id_with_relations(
        self, id: UUID, relations: list[str] | None = None
    ) -> MODEL_TYPE:
        query = select(self.model).where(self.model.id == id)
        if relations:
            for relation in relations:
                query = query.options(joinedload(getattr(self.model, relation)))
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def get_all_with_relations(
        self, relations: list[str] | None = None, **filters: dict[str, Any]
    ) -> list[MODEL_TYPE]:
        query = select(self.model)
        if relations:
            for relation in relations:
                query = query.options(joinedload(getattr(self.model, relation)))
        if filters:
            for field, value in filters.items():
                query = query.where(getattr(self.model, field) == value)
        result = await self._session.execute(query)
        return result.scalars().unique().all()

    async def update(self, id: UUID, data: dict[str, Any] | PYDANTIC_TYPE) -> MODEL_TYPE | None:
        if isinstance(data, PydanticBaseModel):
            data = data.model_dump()

        query = update(self.model).where(self.model.id == id).values(**data).returning(self.model)
        result = await self._session.execute(query)
        if not self._session.in_transaction():
            await self._session.commit()
        return result.scalar_one_or_none()

    async def delete(self, id: UUID) -> bool:
        query = delete(self.model).where(self.model.id == id)
        result = await self._session.execute(query)
        if not self._session.in_transaction():
            await self._session.commit()
        return result.rowcount > 0
