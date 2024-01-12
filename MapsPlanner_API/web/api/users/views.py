from logging import getLogger
from typing import Annotated, Optional


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.requests import Request

from MapsPlanner_API.db.dependencies import get_db_session
from MapsPlanner_API.db.models.Marker import MarkerORM
from MapsPlanner_API.db.models.Session import SessionORM
from MapsPlanner_API.db.models.Trip import TripORM
from MapsPlanner_API.db.models.User import UserORM
from MapsPlanner_API.web.api.users.schema import User, UserDetails, UserUpdateRequest
from MapsPlanner_API.web.api.users.utils import validate_request

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
async def user_details(
    user: Annotated[UserORM, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    user_id: int,
) -> UserDetails:
    validate_request(user, user_id)

    if user := await db.get(UserORM, user_id):
        return await UserDetails.build_from_orm(db, user)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No Such user."
        )


@router.patch("/{user_id}")
async def update_user(
    user: Annotated[UserORM, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    user_id: int,
    payload: UserUpdateRequest,
):
    validate_request(user, user_id)
    update_fields = payload.model_dump(exclude_none=True)

    query = update(UserORM).where(UserORM.id == user_id).values(**update_fields)
    update_result = await db.execute(query)

    if update_result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )
    else:
        updated_user = await db.get(UserORM, user_id)
        return updated_user.to_api()
