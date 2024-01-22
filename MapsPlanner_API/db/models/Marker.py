from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from MapsPlanner_API.db.base import Base
from MapsPlanner_API.web.api.markers.schema import EMarkerCategory, Marker


class MarkerORM(Base):
    """
    This is the markers ORM that we point on the map.
    User can define his own markers, to view later on
    """

    __tablename__ = "markers"

    id: Mapped[int] = mapped_column(primary_key=True)
    trip_id: Mapped[int] = mapped_column(ForeignKey("trips.id"))
    trip: Mapped["TripORM"] = relationship("TripORM", back_populates="markers")
    category: Mapped[int] = mapped_column(Integer())
    title: Mapped[str] = mapped_column(String())
    description: Mapped[str] = mapped_column(String())
    latitude: Mapped[float] = mapped_column(Float())
    longitude: Mapped[float] = mapped_column(Float())

    def to_api(self) -> Marker:
        return Marker(
            id=self.id,
            trip_id=self.trip_id,
            category=EMarkerCategory(self.category),
            title=self.title,
            description=self.description,
            latitude=self.latitude,
            longitude=self.longitude,
        )

    def __str__(self):
        return f"Marker [#{self.id}] for trip [#{self.trip_id}]"

    def __repr__(self):
        return str(self)
