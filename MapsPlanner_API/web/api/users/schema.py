from datetime import date, datetime
from typing import Optional

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from MapsPlanner_API.db.models.User import EGender, UserORM
from MapsPlanner_API.web.api.query_filters.date_range import DateRangeFilterMixin


class User(BaseModel):
    id: int
    first_name: str
    last_name: str
    full_name: str
    email: str
    profile_picture: Optional[str]
    is_active: bool
    is_administrator: bool


class UserDetails(User):
    register_date: datetime
    birth_date: Optional[date]
    gender: Optional[EGender]
    full_name: str
    total_trips: int
    total_markers: int

    @classmethod
    async def build_from_orm(cls, db: AsyncSession, user: "UserORM") -> "UserDetails":

        from MapsPlanner_API.db.models.Marker import MarkerORM
        from MapsPlanner_API.db.models.Trip import TripORM

        total_trips_query = (
            select(func.count()).select_from(TripORM).where(TripORM.user_id == user.id)
        )

        total_trips_result = await db.execute(total_trips_query)

        total_markers_query = (
            select(func.count())
            .select_from(MarkerORM)
            .where(TripORM.user_id == user.id)
            .join(TripORM, MarkerORM.trip_id == TripORM.id)
        )

        total_markers_result = await db.execute(total_markers_query)

        return UserDetails(
            **user.to_api().model_dump(),
            register_date=user.register_date,
            total_trips=total_trips_result.scalar(),
            total_markers=total_markers_result.scalar(),
            birth_date=user.birth_date,
            gender=user.gender.value if user.gender else None,
        )


class UserUpdateRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    profile_picture: Optional[str] = None
    birth_date: Optional[date] = None
    gender: Optional[EGender] = None


class UserFilter(DateRangeFilterMixin, Filter):
    email__ilike: Optional[str] = None
    full_name__ilike: Optional[str] = None
    gender: Optional[EGender] = None

    search: Optional[str] = None

    class Constants(Filter.Constants):
        model = UserORM
        search_model_fields = ["full_name", "email"]
