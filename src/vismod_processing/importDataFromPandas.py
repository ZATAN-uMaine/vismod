import os
from datetime import datetime
import logging
import pandas as pd

from vismod_processing.influx_cli import VismodInfluxBuilder

"""
    # Team ZATAN 2024
    # To learn more about InfluxDB's Python Client API visit:
    Docs:
    https://influxdb-client.readthedocs.io/en/stable/api.html#writeapi
    Repo Readme:
    https://github.com/influxdata/influxdb-client-python/blob/master/README.md#writes
"""

# data fields that are *not* strain levels on a node
WEATHER_COLUMNS = [
    "External-Wind-Speed",
    "External-Wind-Direction",
    "External-Temperature",
]


def df_to_influx_format(data_frame: pd.DataFrame):
    """
    Put the big DataFrame is a series of frames
    in a nice format for Influx.

    Expects the data to already be converted and averaged.
    """

    # drop the node temp columns
    for col in data_frame.columns:
        if "-TEMP" in col:
            data_frame = data_frame.drop(col, axis=1)

    results = []
    for col in data_frame.columns:
        sparse_frame = pd.DataFrame(index=data_frame.index)
        sparse_frame["_value"] = data_frame[col]
        sparse_frame["node"] = col
        for w in WEATHER_COLUMNS:
            sparse_frame[w] = data_frame[w]
        # sometimes there are NaNs in the external sensor date
        # TODO: should we actually drop the whole row?
        sparse_frame = sparse_frame.dropna()
        results.append(sparse_frame)

    logging.info(f"Processed data frame ({data_frame.shape}) for influx")
    return results


def upload_data_frame(data_frame: pd.DataFrame):
    """
    Uploads a pandas data frame to Influx.
    Assumes the frame contains a string field called Node

    List of all sensors as of 3.21/24
    "10A-Left", "10A-Right", "10A-TEMP",
                    "10B-Left", "10B-Right", "10B-TEMP",
                    "17A-Left", "17A-Right", "17A-TEMP",
                    "17B-Left", "17B-Right", "17B-TEMP",
                    "2A-Left", "2A-Right", "2A-TEMP",
                    "2B-Left", "2B-Right", "2B-TEMP",
                    "External-Temperature",
                    "External-Wind-Direction",
                    "External-Wind-Speed"
    """
    # Load database secrets
    zatan_bucket = os.environ.get("INFLUXDB_V2_BUCKET")

    # Initialize Database Client
    node_name = data_frame.iloc[0]["node"]
    logging.info(
        f"=== Ingesting DataFrame for Node {node_name} batching API ==="
    )
    start_time = datetime.now()

    with VismodInfluxBuilder() as cli:
        cli.write().write(
            bucket=zatan_bucket,
            record=data_frame,
            # Fields are the columns that are not identified as tags.
            data_frame_tag_columns=["node"],
            data_frame_measurement_name="NodeStrain",
        )

    logging.info(f"Import finished in: {datetime.now() - start_time}")
