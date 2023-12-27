from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from MapsPlanner_API.db.models.Marker import MarkerORM
from MapsPlanner_API.db.models.User import UserORM


async def validate_marker_for_user(
    db: AsyncSession, user: UserORM, marker_id: int
) -> Optional[MarkerORM]:
    user_trips_ids = [trip.id for trip in await user.awaitable_attrs.trips]
    query = select(MarkerORM).where(
        MarkerORM.id == marker_id, MarkerORM.trip_id.in_(user_trips_ids)
    )

    result = await db.execute(query)
    return result.scalar_one_or_none()
