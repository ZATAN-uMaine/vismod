import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

# Team Zatan 2024
# To learn more about InfluxDB's Python Client API visit:
"""
    Docs:
    https://influxdb-client.readthedocs.io/en/stable/api.html#writeapi
    Repo Readme:
    https://github.com/influxdata/influxdb-client-python/blob/master/README.md#writes
"""

# Load environment
load_dotenv(dotenv_path=Path(".env"))

# Get the current date
current_date = datetime.now().date()
file_name = "{log_date}_influx_db_logs.txt".format(log_date=current_date)

# Enable logging for DataFrame serializer
logger_serializer = logging.getLogger(
    "influxdb_client.client.write.dataframe_serializer"
)
logger_serializer.setLevel(level=logging.DEBUG)
handler = logging.FileHandler(file_name)  # This sets the logging filename 
handler.setFormatter(logging.Formatter("%(asctime)s | %(message)s"))
logger_serializer.addHandler(handler)

# Load database secrets
zatan_token = os.environ.get("INFLUXDB_V2_TOKEN")
organization = os.environ.get("INFLUXDB_V2_ORG")
link = os.environ.get("INFLUXDB_V2_URL")
zatan_bucket = os.environ.get("INFLUXDB_V2_BUCKET")

# set paths for necessary files
# path_to_file = "../../tests/081523.tdms"
# calibration_table_path = "/raw-DAQ-files/sensorCalib.xlsx"

"""
This method takes a dataframe (df), and a bucket for input.
Its purpose is to upload a dataframe to the database.
"""


def upload_data_frame(df, bucket):
    # Initialize data frame
    data_frame = df
    bucket = zatan_bucket
    """
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
    # Initialize Database Client
    print("=== Received data_frame ===")
    # print(data_frame)
    print()
    print("=== Ingesting DataFrame via batching API ===")
    print()
    start_time = datetime.now()
    with InfluxDBClient(url=link, token=zatan_token, org=organization) as cli:
        # Use batching API
        with cli.write_api(write_options=SYNCHRONOUS) as write_api:
            write_api.write(
                bucket=bucket,
                record=data_frame,
                # Fields are the columns that are not identified as tags.
                data_frame_tag_columns=[
                 #    "External-Wind-Speed",
                 #    "External-Wind-Direction",
                 #    "External-Temperature",
                ],
                data_frame_measurement_name="PNB_Reading",
            )

            print()
            print("Waiting to finish ingesting DataFrame...")
            print()

    print()
    print(f"Import finished in: {datetime.now() - start_time}")
    print()
    return
