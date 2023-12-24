from typing import Annotated, List

import sqlalchemy.exc
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import Response

from MapsPlanner_API.db.dependencies import get_db_session
from MapsPlanner_API.db.models.Trip import TripORM
from MapsPlanner_API.db.models.User import UserORM
from MapsPlanner_API.web.api.trips.schema import (
    APITripCreationRequest,
    Trip,
    TripDetails,
)
from MapsPlanner_API.web.api.users.views import get_current_user

router = APIRouter(prefix="/trips", tags=["Trips"])


@router.get("/")
async def get_trips(
    user: Annotated[UserORM, Depends(get_current_user)],
):
    # TODO: Apply filters and pagination
    trips_orm: List[TripORM] = await user.awaitable_attrs.trips
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
                # TODO: Maybe there's a way to automatically extend TripDetails from `trip_card`?
                id=trip_card.id,
                name=trip_card.name,
                picture=trip_card.picture,
                creation_date=trip_card.creation_date,
                user_id=trip_card.user_id,
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
) -> dict:
    no_result_exception = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"Trip #{trip_id} not found."
    )

    try:
        trip = await db.get_one(TripORM, trip_id)
        if trip.is_accessible_to_user(user):
            await db.delete(trip)
            response.status_code = status.HTTP_204_NO_CONTENT
            return {}
        else:
            raise no_result_exception
    except sqlalchemy.exc.NoResultFound:
        raise no_result_exception
