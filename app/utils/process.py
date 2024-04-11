import asyncio
from collections import defaultdict
from os.path import dirname, abspath
from pathlib import Path

import pandas as pd
from scipy.spatial import KDTree

from .constants import CACHE_DF_FILE, NTW_TOWERS_GPS_COORDINATES
from ..async_client.APIAdresse import APIAdresse as AsyncAdresse


class Process:

    def __init__(self, cache_path: Path = None):

        self.api_adresse = AsyncAdresse()
        self.rooth_path = Path(dirname(dirname(dirname(abspath(__file__)))))
        self.data_path = self.rooth_path.joinpath("public")
        # the cache data where are stored the location coordinates of network towers in France
        self.cache_path = self.data_path.joinpath(CACHE_DF_FILE) if not cache_path else self.rooth_path.joinpath(cache_path)

    async def initialize_cache_data(self):
        """
        This method pickles the DataFrame object which contain the location information of french network towers.
        The data from the file is necessary (GPS coordinates of the network towers) for the network coverage.
        Note: The source csv data has been processed using the conversion from lamber93 into GPS format
            of the x,y coordinates.
        """
        if not self.cache_path.exists():
            # pandas library is used in order to speed up the processing of extra large amount of data
            tower_locations = pd.read_csv(self.data_path.joinpath(NTW_TOWERS_GPS_COORDINATES))
            # serialize the DataFrame object
            tower_locations.to_pickle(self.cache_path)

    @staticmethod
    def find_nearest_neighbor(df_group: pd.DataFrame, lat: float, lon: float, nb_nearest_neighbours: int) -> pd.DataFrame:
        """
        This method uses a binary tree in order to search efficiently among the data the nearest from the network
        operators locations in France.
        It finds the 3 nearest neighbours of a network operator
        :param nb_nearest_neighbours: (int) number of nearest neighbours
        :param df_group: (pandas.DataFrame) the data per network operator
        :param lat: (float) the latitude of the location
        :param lon: (float) the longitude of the location
        :return: The nearest network towers per network operator within the different network coverage for the
            given latitude, longitude
        """
        # ndarray
        tower_latitudes = df_group['y_gps'].to_numpy()
        tower_longitudes = df_group['x_gps'].to_numpy()
        # Create the k-d tree for a group on the gps coordinates
        tree = KDTree(list(zip(tower_latitudes, tower_longitudes)))

        # Query the tree for 2-dimension, and get the 3 first nearest index of the network operator
        # information
        nearest_idx = tree.query([lat, lon], k=nb_nearest_neighbours)[1]
        return df_group.iloc[nearest_idx] if nb_nearest_neighbours > 1 else df_group.iloc[[nearest_idx]]


    async def calculate_network_coverages(
            self,
            payload: dict,
            nb_nearest_neighbours: int
    ) -> dict:
        """
        Calculates the 3 nearest network towers for each network operator proposing the network coverage for
            each given location coordinates of address.
        :param nb_nearest_neighbours:
        :param payload: (dict) dictionary of addresses
        :return: dictionary of addresses ids having for each network operator the 3 nearest network towers
        """
        # initialize the result
        result = {add_id: defaultdict(list) for add_id in payload.keys()}
        addresses = await asyncio.gather(*(self.api_adresse.get_address_coordinates(query=value) for value in payload.values()))

        # load the pickled DataFrame object where are stored the location coordinates of network towers in France
        df = pd.read_pickle(self.cache_path)
        for add_id, add_coordinates in zip(payload.keys(), addresses):
            # Apply the function find_nearest_neighbour to each group by network operator in order to get the 3 nearest
            # neighbours where the center location is the given gps coordinates of the address
            nearest_per_operator = df.groupby('Operateur')[df.columns.difference(['Operateur'])].apply(
                self.find_nearest_neighbor,
                lat=add_coordinates.get("y"),
                lon=add_coordinates.get("x"),
                nb_nearest_neighbours=nb_nearest_neighbours
            )
            # convert the float values to string of booleans so that there is more comprehensive way of the network coverage
            nearest_per_operator[["2G", "3G", "4G"]] = nearest_per_operator[["2G", "3G", "4G"]].map(
                lambda x: str(bool(x)).lower()
            )
            # get the corresponding addresses from the network operators' gps coordinates
            data_api_adresses = await asyncio.gather(
                *(self.api_adresse.get_coordinates_address(lon=x, lat=y)
                for x, y in zip(
                    nearest_per_operator["x_gps"].to_numpy(),
                    nearest_per_operator["y_gps"].to_numpy()
                ))
            )
            # treat the data so that there are for each given address and network operator the 3 nearest network towers
            # offering the network coverage within their addresses
            for (operator, data), address in zip(nearest_per_operator[["2G", "3G", "4G"]].iterrows(), data_api_adresses):
                # initial data is Series that holds information for 2G, 3G, 4G only
                # retrieve the address from the gps coordinates of the network tower, add it to the data
                data["address"] = address
                # operator is a tuple of (str: name of operator; int: index in the DataFrame)
                # data is Series
                result[add_id][operator[0]].append(data.to_dict())

        return result
