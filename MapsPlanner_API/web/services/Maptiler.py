import requests

from MapsPlanner_API.settings import settings


class MaptilerClient:
    api_host = "https://api.maptiler.com/geocoding"

    def geocoding(self, query: str, exact: bool = False):
        response = requests.get(
            f"{self.api_host}/{query}",
            params={
                "proximity": "ip",
                "fuzzyMatch": not exact,
                "key": settings.maptiler_api_key,
            },
        )

        response.raise_for_status()

        return response.json()


maptiler_client = MaptilerClient()
