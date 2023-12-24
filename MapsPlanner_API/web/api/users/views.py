from logging import getLogger
from typing import Annotated, Optional


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.requests import Request

from MapsPlanner_API.db.dependencies import get_db_session
from MapsPlanner_API.db.models.Session import SessionORM
from MapsPlanner_API.db.models.User import UserORM
from MapsPlanner_API.web.api.users.schema import User

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
