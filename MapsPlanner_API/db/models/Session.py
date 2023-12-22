import binascii
import os
from datetime import datetime
from typing import Optional, Tuple

from sqlalchemy import String, func, DateTime, ForeignKey, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from MapsPlanner_API.db.base import Base
from MapsPlanner_API.db.models.User import UserORM


class SessionORM(Base):
    __tablename__ = "sessions"

    DEFAULT_TOKEN_LENGTH = 64

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped[UserORM] = relationship(UserORM, backref="tokens")

    token: Mapped[str] = mapped_column(String, primary_key=True)
    creation_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    @classmethod
    def _generate_token(cls, length: int = DEFAULT_TOKEN_LENGTH):
        return binascii.hexlify(os.urandom(length // 2)).decode()

    @classmethod
    async def create_session(cls, db: AsyncSession, user: UserORM) -> str:
        token = cls._generate_token()
        session: SessionORM = SessionORM(user=user, token=token)
        db.add(session)
        await db.commit()
        return token

    @classmethod
    async def get_user(cls, db: AsyncSession, token: str) -> Optional[UserORM]:
        query = (
            select(SessionORM, UserORM)
            .where(SessionORM.token == token)
            .join(UserORM, UserORM.id == SessionORM.user_id)
        )
        fetch_result: Optional[Tuple[SessionORM, UserORM]] = (
            await db.execute(query)
        ).fetchone()

        if fetch_result:
            return fetch_result[1]  # This is the user.
