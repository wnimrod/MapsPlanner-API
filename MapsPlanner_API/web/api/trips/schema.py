import datetime
from typing import List, Optional
from urllib.parse import urlparse

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel, field_validator

from MapsPlanner_API.db.models import TripORM
from MapsPlanner_API.utils import image_url_as_base64
from MapsPlanner_API.web.api.markers.schema import Marker
from MapsPlanner_API.web.api.query_filters.date_range import DateRangeFilterMixin
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

    @field_validator("picture")
    def validate_picture(cls, picture: Optional[str]) -> Optional[str]:
        """
        We don't want to store URL references.
        Instead, we will take a copy of the image and store it on the DB.

        @param: picture - can be either None, base64 image, or url to an image.
        @returns base64 image blob.
        """

        if picture is None:
            return None

        is_url = bool(urlparse(picture).netloc)

        if is_url:
            return image_url_as_base64(picture, raise_on_error=False)

        return picture


class TripFilter(DateRangeFilterMixin, Filter):
    name__ilike: Optional[str] = None
    description__ilike: Optional[str] = None

    search: Optional[str] = None

    class Constants(Filter.Constants):
        model = TripORM
        search_model_fields = ["name", "description"]
