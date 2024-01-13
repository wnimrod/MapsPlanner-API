from typing import Dict, Any

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Mapped, mapped_column
from MapsPlanner_API.db.meta import meta
from MapsPlanner_API.db.models.types import TChanges
from MapsPlanner_API.settings import settings

engine = create_engine(str(settings.db_url), connect_args={})
dbsession = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    """Base for all models."""

    metadata = meta

    def assign(self, changes: Dict[str, Any]):
        for field, updated_value in changes.items():
            setattr(self, field, updated_value)

        return self

    def diff(self, changes: Dict[str, Any]) -> Dict[str, TChanges]:
        """
        Returns a TChanges dict between the object and the changes.
        """

        return {
            field: {"before": before, "after": after}
            for field, after in changes.items()
            if after != (before := getattr(self, field))
        }
