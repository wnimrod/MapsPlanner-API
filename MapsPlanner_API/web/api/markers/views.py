from typing import Annotated, List, Optional

import sqlalchemy.exc
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import Response

from MapsPlanner_API.db.dependencies import get_db_session
from MapsPlanner_API.db.models.AuditLog import EAuditLog
from MapsPlanner_API.db.models.Marker import MarkerORM
from MapsPlanner_API.db.models.Trip import TripORM
from MapsPlanner_API.db.models.User import UserORM
from MapsPlanner_API.utils import Timer
from MapsPlanner_API.web import api_logger
from MapsPlanner_API.web.api.dependencies import TAuditLogger, get_audit_logger, get_current_user
from MapsPlanner_API.web.api.markers.logic import MarkerLogic
from MapsPlanner_API.web.api.markers.schema import (
    APIMarkerCreationRequest,
    APIMarkerGenerationRequest,
    APIMarkerUpdateRequest,
    Marker,
)
from MapsPlanner_API.web.api.markers.transformers import MarkerTransformer
from MapsPlanner_API.web.api.markers.utils import validate_marker_for_user
from MapsPlanner_API.web.api.trips.utils import validate_trip_for_user

router = APIRouter(prefix="/markers", tags=["Markers"])


@router.get("/{marker_id}")
async def get_marker(
    marker_id: int,
    user: Annotated[UserORM, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> Marker:
    marker = await validate_marker_for_user(db, user, marker_id)
    if not marker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Marker #{marker_id} not found.",
        )

    return marker.to_api()


@router.get("/{trip_id}")
async def get_trip_markers(
    trip_id: int,
    user: Annotated[UserORM, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> List[Marker]:
    no_result_exception = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Trip #{trip_id} not found.",
    )

    try:
        trip_orm: TripORM = await db.get_one(TripORM, trip_id)
        if trip_orm.is_accessible_to_user(user):
            markers_query = select(MarkerORM).where(MarkerORM.trip_id == trip_id)
            markers_orm = (await db.scalars(markers_query)).all()
            print(markers_orm)

            return [marker_orm.to_api() for marker_orm in markers_orm]
        else:
            raise no_result_exception
    except sqlalchemy.exc.NoResultFound:
        raise no_result_exception


@router.post("/")
async def create_markers(
    payload: List[APIMarkerCreationRequest],
    response: Response,
    user: Annotated[UserORM, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> List[Marker]:
    # Sanitize markers -- only allowed trips are count.
    allowed_trips_query = (
        select(TripORM.id).where(TripORM.user_id == user.id).distinct(TripORM.id)
    )

    allowed_trip_ids = (await db.scalars(allowed_trips_query)).all()

    valid_creation_requests = [
        creation_request
        for creation_request in payload
        if creation_request.trip_id in allowed_trip_ids
    ]

    markers_orm = MarkerTransformer.marker_creation_requests_to_markers(
        valid_creation_requests,
    )

    db.add_all(markers_orm)
    await db.commit()

    response.status_code = status.HTTP_201_CREATED
    return [marker_orm.to_api() for marker_orm in markers_orm]


@router.post("/{trip_id}/generate-markers")
async def generate_markers(
    trip_id: int,
    payload: APIMarkerGenerationRequest,
    user: Annotated[UserORM, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    audit: Annotated[TAuditLogger, Depends(get_audit_logger)],
) -> List[Marker]:
    assert trip_id == payload.trip_id

    trip: TripORM = await validate_trip_for_user(
        db,
        user,
        trip_id,
        raise_on_not_found=True,
    )

    generate_error: Optional[str] = None
    markers: List[MarkerORM]

    with Timer() as timer:
        try:
            api_logger.debug("Generating Markers with ChatGPT ...")
            markers = await MarkerLogic.generate_markers_suggestions(
                db,
                trip,
                payload.categories,
            )
            api_logger.debug("Finished Markers generation with ChatGPT ...")
        except Exception as e:
            generate_error = str(e)
            api_logger.error(
                f"Failed to generate markers  with ChatGPT: {generate_error}",
            )

    await audit(
        action=EAuditLog.ChatGPTQuery,
        target=trip,
        query_time=timer.total,
        error=generate_error,
    )

    return [marker.to_api() for marker in markers]


@router.patch("/{marker_id}")
async def update_marker(
    marker_id: int,
    payload: APIMarkerUpdateRequest,
    user: Annotated[UserORM, Depends(get_current_user)],
    audit: Annotated[TAuditLogger, Depends(get_audit_logger)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> Marker:
    marker: Optional[MarkerORM] = await validate_marker_for_user(db, user, marker_id)

    if marker is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Marker not found.",
        )

    update_fields = payload.model_dump(exclude_none=True)
    changes = marker.diff(update_fields)
    marker.assign(update_fields)
    db.add(marker)
    await db.commit()
    await audit(action=EAuditLog.Modification, target=marker, changes=changes)
    return marker.to_api()


@router.delete("/{marker_id}")
async def delete_marker(
    marker_id: int,
    response: Response,
    user: Annotated[UserORM, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    audit: Annotated[TAuditLogger, Depends(get_audit_logger)],
):
    marker = await validate_marker_for_user(db, user, marker_id)
    if not marker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Marker #{marker_id} not found.",
        )
    await db.delete(marker)
    await audit(action=EAuditLog.Deletion, target=marker)
    response.status_code = status.HTTP_204_NO_CONTENT
