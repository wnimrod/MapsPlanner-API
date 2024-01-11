from logging import getLogger
from typing import Annotated, Optional


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.requests import Request

from MapsPlanner_API.db.dependencies import get_db_session
from MapsPlanner_API.db.models.Marker import MarkerORM
from MapsPlanner_API.db.models.Session import SessionORM
from MapsPlanner_API.db.models.Trip import TripORM
from MapsPlanner_API.db.models.User import UserORM
from MapsPlanner_API.web.api.users.schema import User, UserDetails

logger = getLogger("app")

router = APIRouter(prefix="/users", tags=["Users"])


async def get_current_user(
    request: Request, db: AsyncSession = Depends(get_db_session)
) -> UserORM:
    token = request.cookies.get("token")
    not_authentication_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Not Authenticated."
    )

    if not token:
        raise not_authentication_exception

    session: Optional[SessionORM] = await db.get(SessionORM, token)
    user: Optional[UserORM] = None

    if session:
        _user: UserORM = await session.awaitable_attrs.user
        if _user.is_active:
            user = _user

    if user:
        return user
    raise not_authentication_exception


@router.get("/current")
async def current_user(user: Annotated[UserORM, Depends(get_current_user)]) -> User:
    """
    Returns details of the currently connected user
    """
    return user.to_api()


@router.get("/{user_id}")
async def get_user_details(
    user: Annotated[UserORM, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    user_id: int,
) -> UserDetails:
    not_found_exception = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="No Such user."
    )

    if not (user_id == user.id or user.is_administrator):
        raise not_found_exception

    if user := await db.get(UserORM, user_id):
        total_trips_query = (
            select(func.count()).select_from(TripORM).where(TripORM.user_id == user_id)
        )
        total_trips_result = await db.execute(total_trips_query)

        total_markers_query = (
            select(func.count())
            .select_from(MarkerORM)
            .where(TripORM.user_id == user_id)
            .join(TripORM, MarkerORM.trip_id == TripORM.id)
        )

        total_markers_result = await db.execute(total_markers_query)

        return UserDetails(
            **user.to_api().model_dump(),
            register_date=user.register_date,
            fullname=f"{user.first_name} {user.last_name}",
            total_trips=total_trips_result.scalar(),
            total_markers=total_markers_result.scalar(),
        )
    else:
        raise not_found_exception
