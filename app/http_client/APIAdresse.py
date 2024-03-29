import logging
from functools import lru_cache
from typing import Generator

from requests import request


class APIAdresse:
    def __init__(self):
        self.api_url = "https://api-adresse.data.gouv.fr"
        self.search_address_url = f"{self.api_url}/search"
        self.reverse_address_url = f"{self.api_url}/reverse"
        self.logger = logging.getLogger("api")

    def send_request(
            self, method: str, url: str, params: dict = None, data: dict = None, headers: dict = None
    ) -> dict:
        """
        Sends a request using the requests.request method defining some of the necessary parameters below
        :param method: (str) it can be GET, POST, PUT, DELETE, PATCH, OPTIONS, HEAD
        :param url: (str) the url on which the request is sent
        :param params: (dict, optional) the parameters to be sent in the query of the request
        :param data: (dict, optional) the data to be sent in the body of the request
        :param headers: (dict, optional) the HTTP headers to be sent
        :return: dictionary as json of the response
        """
        try:
            response = request(method=method, url=url, headers=headers, data=data, params=params)
        except Exception as exp:
            self.logger.error(f"Error on request: {exp}")
            return {}

        if response.status_code == 200:
            return response.json()
        else:
            content_dict = response.json()
            self.logger.error(f"Error code: {response.status_code}, {content_dict}")
            return {}

    def get_address_coordinates(self, query: str) -> dict:
        """
        Retrieve the gps coordinates x, y of an address
        :param query: the address
        :return: dictionary of coordinates
        :rtype: dict
        """
        response = self.send_request(method="GET", url=self.search_address_url, params={"q": query})
        features = response.get("features", [])
        if features:
            coordinates = features[0].get("geometry", {}).get("coordinates", [])
            return {"x": coordinates[0], "y": coordinates[1]} if coordinates else {}
        return {}

    @lru_cache(maxsize=None)
    def get_coordinates_address(self, lon: float, lat: float) -> str:
        """
        Retrieve the address from given gps coordinates x, y
        :param lon: the gps coordinate for x
        :param lat: the gps coordinate for y
        :return: address
        :rtype: str
        """
        response = self.send_request(method="GET", url=self.reverse_address_url, params={"lon": lon, "lat": lat})
        features = response.get("features", [])
        if features:
            return features[0].get("properties", {}).get("label", "Address not found")
        return "Address not found"

    def get_all_coordinates_address(self, **kwargs) -> Generator:
        """
        Generate the addresses upon given gps coordinates x, y
        :return: Generator of string of addresses
        :rtype: Generator
        """
        for data in kwargs["data"]:
            lon, lat = data
            yield self.get_coordinates_address(lon=lon, lat=lat)
