from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from MapsPlanner_API.db.models.Marker import MarkerORM
from MapsPlanner_API.db.models.User import UserORM


async def validate_marker_for_user(
    db: AsyncSession, user: UserORM, marker_id: int
) -> Optional[MarkerORM]:
    where_clause = [MarkerORM.id == marker_id]
    if not user.is_administrator:
        user_trips_ids = [trip.id for trip in await user.awaitable_attrs.trips]
        where_clause.append(MarkerORM.trip_id.in_(user_trips_ids))

    query = select(MarkerORM).where(*where_clause)

    result = await db.execute(query)
    return result.scalar_one_or_none()
