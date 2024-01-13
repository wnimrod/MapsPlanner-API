from functools import partial
from typing import Annotated, Callable, Any, Awaitable, List

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.requests import Request
from typing_extensions import Optional

from MapsPlanner_API.db.dependencies import get_db_session
from MapsPlanner_API.db.models.AuditLog import AuditLogORM
from MapsPlanner_API.db.models.Session import SessionORM
from MapsPlanner_API.db.models.User import UserORM


TAuditLogger = Callable[[...], Awaitable[Any]]


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


async def get_audit_logger(
    user: Annotated[UserORM, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> TAuditLogger:

    return partial(AuditLogORM.log, db, user=user)
