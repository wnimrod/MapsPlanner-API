from enum import IntEnum
from typing import Optional, List

from pydantic import BaseModel


class EMarkerCategory(IntEnum):
    Nature = 0
    Shopping = 1
    Restaurants = 2
    Parks = 3
    Beach = 4
    PublicTransportation = 5


class Marker(BaseModel):
    id: int
    trip_id: int
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


class APIMarkerUpdateRequest(BaseModel):
    category: Optional[EMarkerCategory] = None
    title: Optional[str] = None
    description: Optional[str] = None


class APIMarkerGenerationRequest(BaseModel):
    trip_id: int
    categories: List[EMarkerCategory]
