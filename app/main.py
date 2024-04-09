from pathlib import Path

import pandas as pd
import uvicorn
from fastapi import FastAPI, Request

from http_client.APIAdresse import APIAdresse
from utils.process import calculate_network_coverages
from utils.settings import get_config_dict

api_adresse = APIAdresse()
app = FastAPI()


def main():
    config_vars = get_config_dict()
    app.state.config = config_vars  # Store the config path in the application state
    uvicorn.run(app, host="127.0.0.1", port=8080)


@app.on_event("startup")
def set_up_cache():
    """
    Set up a cache data on startup event of the server.
    This function pickles the DataFrame object which contain the location information of french network towers.
    The data from the file is necessary (GPS coordinates of the network towers) for the network coverage.
    Note: The source csv data has been processed using the conversion from lamber93 into GPS format
        of the x,y coordinates.

    """
    config_path = app.state.config
    cache_data = Path(config_path["cache_file"])
    if not cache_data.exists():
        # pandas library is used in order to speed up the processing of extra large amount of data
        tower_locations = pd.read_csv(config_path["ntw_towers_gps_coordinates"])
        # serialize the DataFrame object
        tower_locations.to_pickle(cache_data)



@app.post("/search")
async def retrieve_network_coverages(payload: dict, request: Request) -> dict:
    """
    This endpoint serves to get the result of the calculation of the nearest network towers of given
    addresses.
    To begin with, there is a request sent to the API of the Adresse for each given address in order to retrieve the GPS
        coordinates longitude, latitude for easier location.
    Then, the calculation of the nearest network towers is returned.
    :param request: The request of the API
    :param payload: dictionary of addresses for which the search process is done
    :return: dictionary of the nearest network operators and their coverage for the given addresses
    :rtype: dict
    """
    config = request.app.state.config
    # get the gps coordinates for the given addresses through the API Adresse
    addresses = {
        address_id: api_adresse.get_address_coordinates(query=address)
        for address_id, address in payload.items()
    }
    # calculate the network coverages, by passing as arguments the retrieved gps coordinates as well as
    # the cache file holding the network towers' gps coordinates
    result = calculate_network_coverages(addresses, config["cache_file"])

    return result


if __name__ == "__main__":
    main()
