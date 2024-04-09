import os
from datetime import datetime
import logging

import pandas as pd
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

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
        results.append(sparse_frame)

    logging.info(f"Processed data frame ({data_frame.shape}) for influx")
    return results


def write_fields(dictionary):
    """
    Write any dict. to the influx database, new keys create new rows
    """
    # Load database secrets
    zatan_token = os.environ.get("INFLUXDB_V2_TOKEN")
    organization = os.environ.get("INFLUXDB_V2_ORG")
    link = os.environ.get("INFLUXDB_V2_URL")
    zatan_bucket = os.environ.get("INFLUXDB_V2_BUCKET")

    if link is None:
        logging.error("$INFLUXDB_V2_URL not found")
        return

   
    # wrap correctly for influx
    fields = {
        'measurement':'last_modified_times',
        'fields': dictionary
    }

    with InfluxDBClient(url=link, token=zatan_token, org=organization) as cli:
        with cli.write_api(write_options=SYNCHRONOUS) as write_api:
            write_api.write(
                bucket=zatan_bucket,
                record=fields
            )
            logging.info("recording changes...")
            InfluxDBClient.close(cli)


def get_row(rowname):
    # Load database secrets
    zatan_token = os.environ.get("INFLUXDB_V2_TOKEN")
    organization = os.environ.get("INFLUXDB_V2_ORG")
    link = os.environ.get("INFLUXDB_V2_URL")
    zatan_bucket = os.environ.get("INFLUXDB_V2_BUCKET")

    if link is None:
        logging.error("$INFLUXDB_V2_URL not found")
        return

    query = f'from(bucket:"{bucket}") 
        |>range(start: -1h) 
        |> filter(fn:(r) => r._measurement == "last_modified_times")'

    query_result = 'Nothing'

    try:
        with InfluxDBClient(url=link, token=zatan_token, org=organization) as cli:
            with cli.query_api as query_api:
                query = f'from(bucket:"{zatan_bucket}") |'
                logging.info("getting latest timestamp...")
                query_result = query_api.query(query, org=org)
                InfluxDBClient.close(cli)
    except:
        logging.error('query error')
    
    return query_result

def upload_data_frame(data_frame):
    """
    Uploads a pandas data frame to Influx

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
    zatan_token = os.environ.get("INFLUXDB_V2_TOKEN")
    organization = os.environ.get("INFLUXDB_V2_ORG")
    link = os.environ.get("INFLUXDB_V2_URL")
    zatan_bucket = os.environ.get("INFLUXDB_V2_BUCKET")

    if link is None:
        logging.error("$INFLUXDB_V2_URL not found")
        return

    # Initialize Database Client
    logging.info("=== Ingesting DataFrame via batching API ===")
    start_time = datetime.now()
    with InfluxDBClient(url=link, token=zatan_token, org=organization) as cli:
        # Use batching API
        with cli.write_api(write_options=SYNCHRONOUS) as write_api:
            write_api.write(
                bucket=zatan_bucket,
                record=data_frame,
                # Fields are the columns that are not identified as tags.
                data_frame_tag_columns=["node"],
                data_frame_measurement_name="NodeStrain",
            )

            logging.debug("Waiting to finish ingesting DataFrame...")
            InfluxDBClient.close(cli)

    logging.info(f"Import finished in: {datetime.now() - start_time}")
