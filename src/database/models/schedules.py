import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import TIMESTAMP, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.models.BaseModel import BaseModel, get_datetime_UTC

if TYPE_CHECKING:
    from src.database.models.users import Users


class Schedules(BaseModel):
    __tablename__ = "schedules"

    repr_cols = ("id", "medicine_name")

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False
    )

    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )

    medicine_name: Mapped[str] = mapped_column(nullable=False)
    frequency: Mapped[int] = mapped_column(nullable=False)

    start_date: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    end_date: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(nullable=False, default=get_datetime_UTC)

    user: Mapped["Users"] = relationship("Users", back_populates="schedules")
