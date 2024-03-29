import pandas as pd
from fastapi import FastAPI

from .http_client.APIAdresse import APIAdresse
from .utils.process import calculate_network_coverages
from .utils.constants import ROOT_PATH, NTW_TOWERS_GPS_COORDINATES, CACHE_DF_FILE

data_path = ROOT_PATH.joinpath("public")
api_adresse = APIAdresse()
app = FastAPI()


@app.on_event("startup")
def set_up_cache():
    """
    Set up a cache data on startup event of the server.
    This function pickles the DataFrame object which contain the location information of french network towers.
    The data from the file is necessary (GPS coordinates of the network towers) for the network coverage.
    Note: The source csv data has been processed using the conversion from lamber93 into GPS format
        of the x,y coordinates.

    """
    cache_data = data_path.joinpath(CACHE_DF_FILE)
    if not cache_data.exists():
        # pandas library is used in order to speed up the processing of extra large amount of data
        tower_locations = pd.read_csv(data_path.joinpath(NTW_TOWERS_GPS_COORDINATES))
        # serialize the DataFrame object
        tower_locations.to_pickle(cache_data)



@app.post("/search")
async def retrieve_network_coverages(payload: dict) -> dict:
    """
    This endpoint serves to get the result of the calculation of the nearest network towers of given
    addresses.
    To begin with, there is a request sent to the API of the Adresse for each given address in order to retrieve the GPS
        coordinates longitude, latitude for easier location.
    Then, the calculation of the nearest network towers is returned.
    :param payload: dictionary of addresses for which the search process is done
    :return: dictionary of the nearest network operators and their coverage for the given addresses
    :rtype: dict
    """
    # get the gps coordinates for the given addresses through the API Adresse
    addresses = {
        address_id: api_adresse.get_address_coordinates(query=address)
        for address_id, address in payload.items()
    }
    # calculate the network coverages, by passing as arguments the retrieved gps coordinates as well as
    # the cache file holding the network towers' gps coordinates
    result = calculate_network_coverages(addresses, data_path.joinpath(CACHE_DF_FILE))

    return result
