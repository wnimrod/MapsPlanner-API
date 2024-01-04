from typing import Optional

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from MapsPlanner_API.db.models.Trip import TripORM
from MapsPlanner_API.db.models.User import UserORM

from datetime import datetime, timezone


async def validate_trip_for_user(
    db: AsyncSession, user: UserORM, trip_id: int, raise_on_not_found: bool = False
) -> Optional[TripORM]:
    where_clause = [TripORM.id == trip_id]

    if not user.is_administrator:
        user_trips_ids = [trip.id for trip in await user.awaitable_attrs.trips]
        where_clause.append(TripORM.id.in_(user_trips_ids))

    query = select(TripORM).where(*where_clause)

    result = await db.execute(query)
    trip = result.scalar_one_or_none()

    if not trip and raise_on_not_found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found.")
    else:
        return trip


def date_range_param_validator(
    date_range: str,
) -> [Optional[datetime], Optional[datetime]]:
    start, end = date_range.split("-")

    return [
        datetime.fromtimestamp(float(ts), tz=timezone.utc) if ts else None
        for ts in [start, end]
    ]
