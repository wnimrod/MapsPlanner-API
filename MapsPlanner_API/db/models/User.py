import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy import String, DateTime, func, Boolean
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from MapsPlanner_API.db.base import Base
from MapsPlanner_API.web.api.users.schema import User


class UserORM(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String())
    last_name: Mapped[str] = mapped_column(String())
    email: Mapped[str] = mapped_column(String())
    register_date: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    profile_picture: Mapped[str] = mapped_column(String(), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean())

    def __str__(self) -> str:
        return f"User [#{self.id}]: {self.first_name} {self.last_name}"

    def to_api_user(self) -> User:
        return User(
            id=self.id,
            first_name=self.first_name,
            last_name=self.last_name,
            email=self.email,
            profile_picture=self.profile_picture,
            is_active=self.is_active,
        )

    @classmethod
    async def get_user(cls, session: AsyncSession, email: str) -> Optional["UserORM"]:
        query = select(UserORM).where(UserORM.email == email, UserORM.is_active == True)
        result = await session.execute(query)
        return result.scalar_one_or_none()