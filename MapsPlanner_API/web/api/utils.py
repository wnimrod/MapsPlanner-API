import functools
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from MapsPlanner_API.db.dependencies import get_db_session
from MapsPlanner_API.db.models.User import UserORM
from MapsPlanner_API.web.api.query_filters import PAGE_SIZE
from MapsPlanner_API.web.api.users.views import get_current_user


def api_response(ORMEntity):
    def decorator(route):
        @functools.wraps(route)
        async def decorated(
            *args,
            user: Annotated[UserORM, Depends(get_current_user)],
            db: Annotated[AsyncSession, Depends(get_db_session)],
            page: int,
            administrator_mode: bool = False,
            **kwargs,
        ):
            query = await route(*args, user, db, page, **kwargs)
            # Add basic protection
            if not administrator_mode:
                query = query.filter(ORMEntity.user_id == user.id)

            # Add pagination
            query = query.slice(PAGE_SIZE * page, PAGE_SIZE)

            result = await db.execute(query)
            return [orm.to_api() for orm in result.scalars()]

        return decorated

    return decorator
