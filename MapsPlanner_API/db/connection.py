import contextlib

import sqlalchemy.exc
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from MapsPlanner_API.settings import settings

engine = create_async_engine(
    str(settings.db_url),
    echo=settings.db_echo,
    json_serializer=settings.json_serializer,
)
session_factory = async_sessionmaker(
    engine,
    expire_on_commit=False,
)


@contextlib.asynccontextmanager
async def get_session():
    session: AsyncSession = session_factory()

    try:
        yield session.begin().session
    except sqlalchemy.exc.SQLAlchemyError:
        await session.rollback()
    finally:
        await session.close()
