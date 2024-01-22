from typing import List

from MapsPlanner_API.db.models.Marker import MarkerORM
from MapsPlanner_API.web.api.markers.schema import APIMarkerCreationRequest


class MarkerTransformer:
    @classmethod
    def marker_creation_requests_to_markers(
        cls,
        creation_requests: List[APIMarkerCreationRequest],
    ) -> List[MarkerORM]:
        return [
            MarkerORM(
                trip_id=marker_creation_request.trip_id,
                category=marker_creation_request.category.value,
                title=marker_creation_request.title,
                description=marker_creation_request.description,
                latitude=marker_creation_request.latitude,
                longitude=marker_creation_request.longitude,
            )
            for marker_creation_request in creation_requests
        ]
