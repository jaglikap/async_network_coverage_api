from os.path import dirname, abspath
from pathlib import Path

# this is the root path of the project
ROOT_PATH = Path(dirname(dirname(dirname(abspath(__file__)))))
# this is the name of the csv file where are stored the location gps coordinates for each network tower in France
NTW_TOWERS_GPS_COORDINATES = "2018_01_Sites_mobiles_2G_3G_4G_France_metropolitaine_GPS.csv"
NTW_TOWERS_L93_COORDINATES = "2018_01_Sites_mobiles_2G_3G_4G_France_metropolitaine_L93_ver2.csv"
# this is the cache file where will be serialized the DataFrame object of the extra large csv file where are stored the
# location gps information for every network tower in France
CACHE_DF_FILE = "tower_locations.pkl"
