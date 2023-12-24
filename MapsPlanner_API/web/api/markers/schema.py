from enum import IntEnum

from pydantic import BaseModel


class EMarkerCategory(IntEnum):
    nature = 0
    shopping = 1


class Marker(BaseModel):
    id: int
    category: EMarkerCategory
    title: str
    description: str
    latitude: float
    longitude: float


class APIMarkerCreationRequest(BaseModel):
    trip_id: int
    category: EMarkerCategory
    title: str
    description: str
    latitude: float
    longitude: float
