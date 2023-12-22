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
):
    token = request.cookies.get("token")
    not_authentication_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Not Authenticated."
    )

    if not token:
        raise not_authentication_exception

    user: Optional[UserORM] = await SessionORM.get_user(db, token)
    if not user:
        raise not_authentication_exception

    return user.to_api_user()


@router.get("/current")
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    """
    Returns details of the currently connected user
    """
    return current_user
