import datetime
from typing import List

import sqlalchemy
from sqlalchemy import String, DateTime, func, ForeignKey
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import Mapped, mapped_column, relationship

from MapsPlanner_API.db.base import Base
from MapsPlanner_API.db.models.Marker import MarkerORM
from MapsPlanner_API.db.models.User import UserORM


class TripORM(AsyncAttrs, Base):
    """
    This model represents a user trip.
    """

    __tablename__ = "trips"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String())
    description: Mapped[str] = mapped_column(
        String(), server_default=sqlalchemy.text("''")
    )
    picture: Mapped[str | None] = mapped_column(String(), nullable=True)
    creation_date: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Forward relations
    markers: Mapped[List[MarkerORM]] = relationship(
        MarkerORM,
        back_populates="trip",
        order_by="asc(MarkerORM.id)",
    )
    user: Mapped[UserORM] = relationship(UserORM, back_populates="trips")

    def to_api(self, detailed: bool = False) -> "Trip":
        from MapsPlanner_API.web.api.trips.schema import Trip

        trip = Trip(
            id=self.id,
            name=self.name,
            description=self.description,
            picture=self.picture,
            creation_date=self.creation_date,
            user_id=self.user_id,
        )

        if detailed:
            raise NotImplementedError("Need to somehow fetch markers ......")
        else:
            return trip

    def is_accessible_to_user(self, user: UserORM) -> bool:
        return user.is_active and (self.user_id == user.id or user.is_administrator)

    def __str__(self):
        return f"Trip [#{self.id}]: ${self.name}"

    def __repr__(self):
        return str(self)
