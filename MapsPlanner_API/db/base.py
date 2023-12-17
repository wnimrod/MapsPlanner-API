from sqlalchemy.orm import DeclarativeBase
from MapsPlanner_API.db.meta import meta


class Base(DeclarativeBase):
    """Base for all models."""

    metadata = meta
