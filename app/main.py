from fastapi import FastAPI
from .utils.process import Process

process = Process()
app = FastAPI()


@app.on_event("startup")
async def set_up_cache():
    """
    Set up a cache data on startup event of the server.
    This function pickles the DataFrame object which contain the location information of french network towers.
    The data from the file is necessary (GPS coordinates of the network towers) for the network coverage.
    Note: The source csv data has been processed using the conversion from lamber93 into GPS format
        of the x,y coordinates.

    """
    await process.initialize_cache_data()


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
    # calculate the network coverages, by passing as arguments the retrieved gps coordinates as well as
    # the cache file holding the network towers' gps coordinates
    result = await process.calculate_network_coverages(payload=payload, nb_nearest_neighbours=3)

    return result
