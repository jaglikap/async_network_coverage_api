import io
import os
from collections import defaultdict
from pathlib import Path

import pandas as pd
import pytest

from app.http_client.APIAdresse import APIAdresse
from app.utils.constants import ROOT_PATH
from app.utils.process import Process


def init_process():
    return Process(cache_path=Path("tests").joinpath("data").joinpath("pickled_data.pkl"))

test_location_data = ROOT_PATH.joinpath("tests").joinpath("data").joinpath("pickled_data.pkl")

file_data_csv = """Operateur,x,y,2G,3G,4G,x_gps,y_gps
Orange,643536,6859045,0,0,0,2.2308558301658454,48.82898791309985
Bouygues,643538,6854488,1,1,1,2.2314872041011866,48.78800621791439
Orange,643542,6859001,0,0,0,2.230943393408969,48.82859274638305
SFR,643544,6867593,1,1,1,2.229829125192331,48.905858156670575
Free,654160,6867508,0,1,1,2.3746546706655636,48.90593739432726
SFR,654058,6867020,1,1,1,2.373316087868463,48.901541762067914
Bouygues,654438,6866789,1,1,0,2.3785241622997244,48.899491486677576
SFR,643546,6866472,0,1,1,2.2300055273384602,48.89577782875365
Bouygues,643547,6859126,1,0,0,2.2309949158123312,48.829717309784385
SFR,643548,6859171,1,0,0,2.2310025673932508,48.830122082261
Orange,643557,6249230,1,1,0,2.304324468969916,43.33997936932075
SFR,643561,6866191,0,1,0,2.2302474650292434,48.89325225916154
Orange,643569,6866431,0,0,0,2.230324662616711,48.895411154238865
Free,654569,6866161,0,1,1,2.3803781748958466,48.8938533891417
Bouygues,654570,6866161,1,1,1,2.380391813081014,48.89385345970791
Bouygues,654077,6866800,1,1,1,2.37359905734256,48.899564753022446
SFR,654401,6866873,1,1,0,2.3780104697743543,48.900244243301174
Orange,654457,6866820,0,0,0,2.378779989252433,48.899771601141325
SFR,643575,6866061,1,1,0,2.230455673058618,48.89208446287574
Free,643579,6210149,0,1,0,2.3088118645623297,42.988473639375464
SFR,643579,6859021,1,1,1,2.231444714644118,48.82877584632471
SFR,643580,6865946,1,1,0,2.2305391436482043,48.89105076389454
SFR,643580,6865946,0,1,1,2.2305391436482043,48.89105076389454
Orange,643582,6866062,0,0,0,2.230551002623363,48.892094068816746
Orange,643582,7032843,1,1,0,2.207729331739379,50.39066466197236
Orange,643970,6233594,1,1,1,2.3110958638747605,43.199364527953485
Free,643970,6233598,0,1,1,2.311095434807385,43.19940050637446
SFR,652415,6866985,1,1,0,2.350909231683814,48.90110766434586
Orange,654408,6866970,0,0,0,2.378095528150369,48.90111701843907
SFR,644265,6230625,1,1,1,2.315039438906006,43.1726829106211
Orange,644343,6329246,1,1,1,2.3053356956213396,44.06001277479066
Orange,644918,6866029,0,0,1,2.2487750205435786,48.89191300355631
Bouygues,654403,6866651,0,1,1,2.3780616000374857,48.89824803174769
Free,654892,6866646,0,1,1,2.3847317698096275,48.89823751917798
Orange,654406,6866641,0,0,0,2.378103592272793,48.89815831832524
"""

data_test_addresses = ['159 Boulevard Macdonald 75019 Paris', '10 Rue Chana Orloff 75019 Paris',
                       '63 Rue Emile Bollaert 75019 Paris', '159b Avenue de Flandre 75019 Paris',
                       '101 Boulevard Macdonald 75019 Paris', '87 Avenue Victor Hugo 93300 Aubervilliers',
                       '24 Rue Césaria Évora 75019 Paris', '19 Rue Emile Bollaert 75019 Paris',
                       '109p5 109P5 Rue de la Haie Coq 75019 Paris', '25p1 25P1 Quai du Lot 75019 Paris',
                       '109p6 109P6 Rue de la Haie Coq 75019 Paris', '37 Rue de la Gare 75019 Paris']

data_all_address_coordinates = [{'x': 2.378185, 'y': 48.898595}]


def mock_get_all_coordinates_address(self, **kwargs):
    for data in data_test_addresses:
        yield data


def mock_all_address_coordinates(self, **kwargs):
    for data in data_all_address_coordinates:
        yield data

@pytest.mark.parametrize(
    "payload, data_csv, expected",
    [
        pytest.param(
            {},
            """Operateur,x,y,2G,3G,4G,x_gps,y_gps
            """,
            {}
        ),
        pytest.param(
            {"id1": "157 boulevard Mac Donald 75019 Paris"},
            file_data_csv,
            {'id1': defaultdict(list,
                                {'Bouygues': [{'2G': 'false', '3G': 'true', '4G': 'true',
                                               'address': '159 Boulevard Macdonald 75019 Paris'},
                                              {'2G': 'true', '3G': 'true', '4G': 'false',
                                               'address': '10 Rue Chana Orloff 75019 Paris'},
                                              {'2G': 'true', '3G': 'true', '4G': 'true',
                                               'address': '63 Rue Emile Bollaert 75019 Paris'}],
                                 'Free': [{'2G': 'false', '3G': 'true', '4G': 'true',
                                           'address': '159b Avenue de Flandre 75019 Paris'},
                                          {'2G': 'false', '3G': 'true', '4G': 'true',
                                           'address': '101 Boulevard Macdonald 75019 Paris'},
                                          {'2G': 'false', '3G': 'true', '4G': 'true',
                                           'address': '87 Avenue Victor Hugo 93300 Aubervilliers'}],
                                 'Orange': [{'2G': 'false', '3G': 'false', '4G': 'false',
                                             'address': '24 Rue Césaria Évora 75019 Paris'},
                                            {'2G': 'false', '3G': 'false', '4G': 'false',
                                             'address': '19 Rue Emile Bollaert 75019 Paris'},
                                            {'2G': 'false', '3G': 'false', '4G': 'false',
                                             'address': '109p5 109P5 Rue de la Haie Coq 75019 Paris'}],
                                 'SFR': [{'2G': 'true', '3G': 'true', '4G': 'false',
                                          'address': '25p1 25P1 Quai du Lot 75019 Paris'},
                                         {'2G': 'true', '3G': 'true', '4G': 'true',
                                          'address': '109p6 109P6 Rue de la Haie Coq 75019 Paris'},
                                         {'2G': 'true', '3G': 'true', '4G': 'false',
                                          'address': '37 Rue de la Gare 75019 Paris'}]}
                                )
             }
        )
    ]
)
def test_calculate_network_coverages(monkeypatch, payload, data_csv, expected):
    process = init_process()
    tower_locations = pd.read_csv(io.StringIO(data_csv))
    tower_locations.to_pickle(process.cache_path)
    monkeypatch.setattr(APIAdresse, "get_all_coordinates_address", mock_get_all_coordinates_address)
    monkeypatch.setattr(APIAdresse, "get_all_address_coordinates", mock_all_address_coordinates)
    result = process.calculate_network_coverages(payload, 3)
    os.remove(process.cache_path)
    assert result == expected
