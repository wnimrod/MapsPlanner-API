from typing import Annotated, Optional

import sqlalchemy.exc
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import Response

from MapsPlanner_API.db.dependencies import get_db_session
from MapsPlanner_API.db.models.AuditLog import EAuditAction
from MapsPlanner_API.db.models.Trip import TripORM
from MapsPlanner_API.db.models.User import UserORM
from MapsPlanner_API.web.api.dependencies import (
    TAuditLogger,
    get_audit_logger,
    get_current_user,
    get_queryset,
)
from MapsPlanner_API.web.api.query_filters import DateRangeFilter
from MapsPlanner_API.web.api.trips.schema import (
    APITripCreationRequest,
    Trip,
    TripDetails,
)

router = APIRouter(prefix="/trips", tags=["Trips"])


@router.get("/")
async def get_trips(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    query: Annotated[Select, Depends(get_queryset(TripORM))],
    creation_date: Optional[
        DateRangeFilter(
            description='Unix timestamp date range, in format of "start...end".',
            examples=["1704242003-1704328403"],
        )
    ] = (None, None),
    name: Optional[str] = None,
):
    start_filter, end_filter = creation_date

    if start_filter is not None:
        query = query.where(TripORM.creation_date >= start_filter)
    if end_filter is not None:
        query = query.where(TripORM.creation_date <= end_filter)
    if name is not None:
        query = query.where(TripORM.name.ilike(name))

    result = await db.execute(query)
    trips_orm = result.scalars()

    return [trip_orm.to_api() for trip_orm in trips_orm]


@router.get("/{trip_id}")
async def get_trip(
    trip_id: int,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    query: Annotated[Select, Depends(get_queryset(TripORM))],
) -> TripDetails:
    try:
        query = query.where(TripORM.id == trip_id)
        trip_orm: TripORM = (await db.execute(query)).scalar_one()
        trip_card: Trip = trip_orm.to_api()
        markers_orm = await trip_orm.awaitable_attrs.markers

        return TripDetails(
            **trip_card.model_dump(),
            markers=[marker_orm.to_api() for marker_orm in markers_orm],
        )
    except (sqlalchemy.exc.NoResultFound, sqlalchemy.exc.MultipleResultsFound):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trip #{trip_id} not found.",
        )


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
    db: Annotated[AsyncSession, Depends(get_db_session)],
    query: Annotated[Select, Depends(get_queryset(TripORM))],
    audit: Annotated[TAuditLogger, Depends(get_audit_logger)],
) -> dict:
    try:
        query = query.where(TripORM.id == trip_id)
        trip_orm: TripORM = (await db.execute(query)).scalar_one()

        await db.delete(trip_orm)
        await audit(action=EAuditAction.Deletion, target=trip_orm)

        response.status_code = status.HTTP_204_NO_CONTENT
        return {}

    except (sqlalchemy.exc.NoResultFound, sqlalchemy.exc.MultipleResultsFound):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trip #{trip_id} not found.",
        )
