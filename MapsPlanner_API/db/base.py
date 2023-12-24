from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from MapsPlanner_API.db.meta import meta
from MapsPlanner_API.settings import settings

engine = create_engine(str(settings.db_url), connect_args={})
dbsession = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    """Base for all models."""

    metadata = meta
