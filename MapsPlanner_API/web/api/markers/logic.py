import json
from typing import TypedDict, List

from sqlalchemy.ext.asyncio import AsyncSession

from MapsPlanner_API.db.models.Marker import MarkerORM
from MapsPlanner_API.db.models.Trip import TripORM
from MapsPlanner_API.web.api.chatgpt.chatgpt_client import async_chatgpt_client

from MapsPlanner_API.web.api.markers.schema import (
    EMarkerCategory,
    APIMarkerCreationRequest,
)
from MapsPlanner_API.web.api.markers.transformers import MarkerTransformer
from MapsPlanner_API.web.api.trips.schema import Trip


class MarkerLogic:
    @classmethod
    def get_marker_suggestion_prompt(cls, area: str, category: EMarkerCategory) -> str:
        category_prompt_mapper: TypedDict[EMarkerCategory, str] = {
            EMarkerCategory.Nature: "nature sites",
            EMarkerCategory.Shopping: "shopping centers",
            EMarkerCategory.Restaurants: "restaurants",
            EMarkerCategory.Parks: "city parks",
            EMarkerCategory.Beach: "sea beaches",
            EMarkerCategory.PublicTransportation: "Central Transportation Stations",
        }

        return (
            f"Give me the best {category_prompt_mapper[category]} in {area} in flat json array format with fields title, "
            f"description, latitude and longitude."
        )

    @classmethod
    async def generate_markers_suggestions(
        cls, db: AsyncSession, trip: TripORM | Trip, categories: List[EMarkerCategory]
    ) -> List[MarkerORM]:
        queries = [
            cls.get_marker_suggestion_prompt(trip.name, category)
            for category in categories
        ]

        response = await async_chatgpt_client.query(queries)

        marker_creation_requests = []

        for idx, query_response in enumerate(response):
            for suggestion in json.loads(query_response):
                marker_creation_requests.append(
                    APIMarkerCreationRequest(
                        trip_id=trip.id, category=categories[idx], **suggestion
                    )
                )

        markers = MarkerTransformer.marker_creation_requests_to_markers(
            marker_creation_requests
        )

        db.add_all(markers)
        await db.commit()
        return markers
