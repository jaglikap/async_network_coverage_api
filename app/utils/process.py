from collections import defaultdict
from pathlib import Path

import pandas as pd
from scipy.spatial import KDTree
from app.http_client.APIAdresse import APIAdresse

api_adresse = APIAdresse()


def find_nearest_neighbor(df_group: pd.DataFrame, lat: float, lon: float, nb_nearest_neighbours: int) -> pd.DataFrame:
    """
    This function uses a binary tree in order to search efficiently among the data the nearest from the network
    operators locations in France.
    It finds the 3 nearest neighbours of a network operator
    :param nb_nearest_neighbours: (int) number of nearest neighbours
    :param df_group: (pandas.DataFrame) the data per network operator
    :param lat: (float) the latitude of the location
    :param lon: (float) the longitude of the location
    :return: The nearest network towers per network operator within the different network coverage for the
        given latitude, longitude
    """
    # Create the k-d tree for a group on the gps coordinates
    tower_latitudes = df_group['y_gps'].to_numpy()
    tower_longitudes = df_group['x_gps'].to_numpy()
    tree = KDTree(list(zip(tower_latitudes, tower_longitudes)))

    # Query the tree for 2-dimension, and get the 3 first nearest index of the network operator
    # information
    nearest_idx = tree.query([lat, lon], k=nb_nearest_neighbours)[1]
    return df_group.iloc[nearest_idx]


def calculate_network_coverages(addresses: dict, cache_data_path: str) -> dict:
    """
    Calculates the 3 nearest network towers for each network operator proposing the network coverage for
        each given location coordinates of address.
    :param addresses: (dict) dictionary of address location coordinates
    :param cache_data_path: (Path) the cache data where are stored the location coordinates of network towers in France
    :return: dictionary of addresses ids having for each network operator the 3 nearest network towers
    """
    result = {add_id: defaultdict(list) for add_id in addresses.keys()}
    # load the pickled DataFrame object where are stored the location coordinates of network towers in France
    df = pd.read_pickle(cache_data_path)
    for add_id, add_coordinates in addresses.items():
        # Apply the function find_nearest_neighbour to each group by network operator in order to get the 3 nearest
        # neighbours where the center location is the given gps coordinates of the address
        nearest_per_operator = df.groupby('Operateur')[df.columns.difference(['Operateur'])].apply(
            find_nearest_neighbor, lat=add_coordinates.get("y"), lon=add_coordinates.get("x"), nb_nearest_neighbours=3
        )
        # convert the float values to string of booleans so that there is more comprehensive way of the network coverage
        nearest_per_operator[["2G", "3G", "4G"]] = nearest_per_operator[["2G", "3G", "4G"]].map(
            lambda x: str(bool(x)).lower()
        )
        # get the corresponding addresses from the network operators' gps coordinates
        data_api_adresses = api_adresse.get_all_coordinates_address(
            data=list(zip(nearest_per_operator["x_gps"].to_numpy(), nearest_per_operator["y_gps"].to_numpy()))
        )
        # treat the data so that there are for each given address and network operator the 3 nearest network towers
        # offering the network coverage within their addresses
        for (operator, data), address in zip(nearest_per_operator[["2G", "3G", "4G"]].iterrows(), data_api_adresses):
            # retrieve the address from the gps coordinates of the network tower
            data["address"] = address
            result[add_id][operator[0]].append(data.to_dict())

    return result
