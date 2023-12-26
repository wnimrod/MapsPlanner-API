import datetime
from typing import Optional, List

from pydantic import BaseModel

from MapsPlanner_API.web.api.markers.schema import Marker
from MapsPlanner_API.web.api.schema import DateRangeFilter


class Trip(BaseModel):
    id: int
    name: str
    description: str
    picture: str
    creation_date: datetime.datetime
    user_id: int


class TripDetails(Trip):
    markers: List[Marker]


class APITripFilter(BaseModel):
    name: Optional[str] = None  # Can be partial name
    creation_date: Optional[DateRangeFilter] = None


class APITripCreationRequest(BaseModel):
    name: str
    description: Optional[str] = ""
    picture: Optional[str]
