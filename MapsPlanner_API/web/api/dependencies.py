from functools import partial
from typing import Annotated, Any, Awaitable, Callable, Literal, Type

from fastapi import Depends, HTTPException
from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.requests import Request
from typing_extensions import Optional

from MapsPlanner_API.db.base import Base as BaseORM
from MapsPlanner_API.db.dependencies import get_db_session
from MapsPlanner_API.db.models.AuditLog import AuditLogORM
from MapsPlanner_API.db.models.Session import SessionORM
from MapsPlanner_API.db.models.User import UserORM
from MapsPlanner_API.web.api.query_filters import PAGE_SIZE

TAuditLogger = Callable[[...], Awaitable[Any]]


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
) -> UserORM:
    token = request.cookies.get("token")
    not_authentication_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not Authenticated.",
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


def get_queryset(model_class: Type[BaseORM], order_field: Optional[str] = "id"):
    async def _make_dependency(
        user: Annotated[UserORM, Depends(get_current_user)],
        page: Optional[int] = None,
        impersonate_user_id: Optional[int | Literal["all"]] = None,
    ) -> Select:
        query = select(model_class)

        # Access control - Filter by user id
        if impersonate_user_id is None or user.is_administrator is False:
            query = query.where(model_class.user_id == user.id)
        elif impersonate_user_id != "all":
            query = query.where(model_class.user_id == impersonate_user_id)

        # Order results
        if order_field is not None:
            query = query.order_by(getattr(model_class, order_field).desc())

        # Should paginate?
        if page is not None:
            query.slice(PAGE_SIZE * page, PAGE_SIZE)

        return query

    return _make_dependency
