import uuid
from datetime import datetime
from typing import List, TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from src.database.models.BaseModel import BaseModel, get_datetime_UTC

if TYPE_CHECKING:
    from src.database.models.schedules import Schedules


class Users(BaseModel):
    __tablename__ = "users"

    repr_cols = ("id", "name")

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False
    )
    medicine_policy: Mapped[int] = mapped_column(nullable=False, unique=True)
    name: Mapped[str] = mapped_column(nullable=True)

    created_at: Mapped[datetime] = mapped_column(nullable=False, default=get_datetime_UTC)

    schedules: Mapped[List["Schedules"]] = relationship(
        "Schedules", back_populates="user", cascade="all, delete-orphan"
    )
