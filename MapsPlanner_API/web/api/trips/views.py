from typing import Annotated, Optional, Callable

import sqlalchemy.exc
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import Response

from MapsPlanner_API.db.dependencies import get_db_session
from MapsPlanner_API.db.models.AuditLog import EAuditLog
from MapsPlanner_API.db.models.Trip import TripORM
from MapsPlanner_API.db.models.User import UserORM
from MapsPlanner_API.web.api.dependencies import (
    get_current_user,
    TAuditLogger,
    get_audit_logger,
)
from MapsPlanner_API.web.api.query_filters import DateRangeFilter, PAGE_SIZE
from MapsPlanner_API.web.api.trips.schema import (
    APITripCreationRequest,
    Trip,
    TripDetails,
)

router = APIRouter(prefix="/trips", tags=["Trips"])


@router.get("/")
async def get_trips(
    user: Annotated[UserORM, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    page: int = 0,
    creation_date: Optional[
        DateRangeFilter(
            description='Unix timestamp date range, in format of "start...end".',
            examples=["1704242003-1704328403"],
        )
    ] = (None, None),
    user_id: Optional[int] = None,
    name: Optional[str] = None,
):

    query = (
        select(TripORM)
        .where(TripORM.user_id == user.id)
        .order_by(TripORM.creation_date.desc())
        .slice(PAGE_SIZE * page, PAGE_SIZE)
    )

    start_filter, end_filter = creation_date

    if start_filter is not None:
        query = query.where(TripORM.creation_date >= start_filter)
    if end_filter is not None:
        query = query.where(TripORM.creation_date <= end_filter)
    if name is not None:
        query = query.where(TripORM.name.ilike(name))
    if user_id is not None:
        query = query.where(TripORM.user_id == user_id)

    result = await db.execute(query)
    trips_orm = result.scalars()

    return [trip_orm.to_api() for trip_orm in trips_orm]


@router.get("/{trip_id}")
async def get_trip(
    trip_id: int,
    user: Annotated[UserORM, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> TripDetails:
    no_result_exception = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"Trip #{trip_id} not found."
    )

    try:
        trip_orm: TripORM = await db.get_one(TripORM, trip_id)
        if trip_orm.is_accessible_to_user(user):
            trip_card: Trip = trip_orm.to_api()
            markers_orm = await trip_orm.awaitable_attrs.markers
            return TripDetails(
                **trip_card.model_dump(),
                markers=[marker_orm.to_api() for marker_orm in markers_orm],
            )
        else:
            raise no_result_exception
    except sqlalchemy.exc.NoResultFound:
        raise no_result_exception


@router.post("/")
async def create_trip(
    payload: APITripCreationRequest,
    response: Response,
    user: Annotated[UserORM, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> Trip:
    trip_orm = TripORM(
        user_id=user.id,
        name=payload.name,
        description=payload.description,
        picture=payload.picture,
    )

    db.add(trip_orm)
    await db.commit()

    response.status_code = status.HTTP_201_CREATED

    return trip_orm.to_api()


@router.delete("/{trip_id}")
async def delete_trip(
    trip_id: int,
    response: Response,
    user: Annotated[UserORM, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    audit: Annotated[TAuditLogger, Depends(get_audit_logger)],
) -> dict:
    no_result_exception = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"Trip #{trip_id} not found."
    )

    try:
        trip = await db.get_one(TripORM, trip_id)
        if trip.is_accessible_to_user(user):
            await db.delete(trip)
            await audit(action=EAuditLog.Deletion, target=trip)
            response.status_code = status.HTTP_204_NO_CONTENT
            return {}
        else:
            raise no_result_exception
    except sqlalchemy.exc.NoResultFound:
        raise no_result_exception
