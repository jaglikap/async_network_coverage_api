import logging
from functools import lru_cache

import httpx


class APIAdresse:
    def __init__(self):
        self.api_url = "https://api-adresse.data.gouv.fr"
        self.search_address_url = f"{self.api_url}/search"
        self.reverse_address_url = f"{self.api_url}/reverse"
        self.logger = logging.getLogger("api")

    async def send_request(
            self, method: str, url: str, params: dict = None, data: dict = None, headers: dict = None
    ) -> dict:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.request(method=method, url=url, headers=headers, data=data, params=params)
        except Exception as exp:
            self.logger.error(f"Error on request: {exp}")
            return {}

        if response.status_code == 200:
            return response.json()
        else:
            content_dict = response.json()
            self.logger.error(f"Error code: {response.status_code}, {content_dict}")
            return {}

    @lru_cache(maxsize=None)
    async def get_address_coordinates(self, query: str) -> dict:
        response = await self.send_request(method="GET", url=self.search_address_url, params={"q": query})
        features = response.get("features", [])
        if features:
            coordinates = features[0].get("geometry", {}).get("coordinates", [])
            return {"x": coordinates[0], "y": coordinates[1]} if coordinates else {}
        return {}

    @lru_cache(maxsize=None)
    async def get_coordinates_address(self, lon: float, lat: float) -> str:
        response = await self.send_request(method="GET", url=self.reverse_address_url, params={"lon": lon, "lat": lat})
        features = response.get("features", [])
        if features:
            return features[0].get("properties", {}).get("label", "Address not found")
        return "Address not found"
