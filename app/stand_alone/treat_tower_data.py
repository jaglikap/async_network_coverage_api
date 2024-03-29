import argparse
from pathlib import Path

import pyproj
import pandas as pd
from dask import dataframe as dd
from app.utils.constants import ROOT_PATH, NTW_TOWERS_L93_COORDINATES


def lambert93_to_gps_vectorized(df):
    """
    Conversion of lambert93 coordinates into GPS format
    :param df: the dataframe dask on which the conversion will be applied
    :return: The mathematical operation of the lambert93 into GPS conversion by adding two new columns x_gps, y_gps
    """
    lambert = pyproj.Proj('+proj=lcc +lat_1=49 +lat_2=44 +lat_0=46.5 +lon_0=3 +x_0=700000 +y_0=6600000 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs')
    wgs84 = pyproj.Proj('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')
    df['x_gps'], df['y_gps'] = pyproj.transform(lambert, wgs84, df['x'].values, df['y'].values)
    return df

def convert_l93_into_gps(dest_file: Path):
    """
    Convert the lambert93 format of coordinates into GPS.
    It uses pandas and dask libraries in order to speed up the calculation of mathematical transformations and
    generation of new csv file
    :param dest_file:
    """
    path_to_origin_csv = ROOT_PATH.joinpath("public").joinpath(NTW_TOWERS_L93_COORDINATES)
    path_to_destination_csv = ROOT_PATH.joinpath("public").joinpath(dest_file)
    # Load the CSV file into Dask DataFrame
    df = dd.read_csv(path_to_origin_csv)

    # Create a metadata DataFrame that includes the new columns
    meta = df._meta.assign(x_gps=pd.Series(dtype='float64'), y_gps=pd.Series(dtype='float64'))

    # Apply the function
    df = df.map_partitions(lambert93_to_gps_vectorized, meta=meta)

    # Convert Dask DataFrame to Pandas DataFrame
    df = df.compute()

    # Save the result into new CSV file
    df.to_csv(path_to_destination_csv, index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--destfilename", type=str, help="The name of the csv file where the conversion will be generated"
    )
    args = parser.parse_args()

    convert_l93_into_gps(args.destfilename)
