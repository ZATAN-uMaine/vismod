import pandas as pd
import os
import csv
from datetime import datetime, timedelta
import reactivex as rx
from reactivex import operators as ops

from influxdb_client import Point, InfluxDBClient, WriteOptions

# from influxdb_client.client.write_api import SYNCHRONOUS

# InfluxDB Token (NEED TO LEARN HOW TO PUT THIS IN THE ENV AND REFERENCE IT)
# Currently I type INFLUXDB_TOKEN=<token> into the console to load it into the environment prior to running the script


# zatanToken = "ulIEuO_JraLqvnMXRf8qraQRoCQXJKiPD7VCvVUp02JOPGIWU9xNnQU_Bd0-dhM40Je8UtnetLQgUyePT39J5w=="
zatanToken = os.environ.get("INFLUXDB_TOKEN")


# with InfluxDBClient(url="http://influx:8086", token="zatanToken", org="my-org") as _client:
with InfluxDBClient(
    url="http://localhost:8086", token="my-token", org="my-org"
) as _client:
    with _client.write_api(
        write_options=WriteOptions(
            batch_size=500,
            flush_interval=10_000,
            jitter_interval=2_000,
            retry_interval=5_000,
            max_retries=5,
            max_retry_delay=30_000,
            max_close_wait=300_000,
            exponential_base=2,
        )
    ) as _write_client:
        """
        Write Pandas DataFrame
        """
        _now = datetime.utcnow()
        _data_frame = pd.DataFrame(
            data=[["coyote_creek", 1.0], ["coyote_creek", 2.0]],
            index=[_now, _now + timedelta(hours=1)],
            columns=["location", "water_level"],
        )

        _write_client.write(
            "my-bucket",
            "my-org",
            record=_data_frame,
            data_frame_measurement_name="h2o_feet",
            data_frame_tag_columns=["location"],
        )

        """
        Write Dictionary-style object
        """
        _write_client.write(
            "my-bucket",
            "my-org",
            {
                "measurement": "h2o_feet",
                "tags": {"location": "coyote_creek"},
                "fields": {"water_level": 1.0},
                "time": 1,
            },
        )
        _write_client.write(
            "my-bucket",
            "my-org",
            [
                {
                    "measurement": "h2o_feet",
                    "tags": {"location": "coyote_creek"},
                    "fields": {"water_level": 2.0},
                    "time": 2,
                },
                {
                    "measurement": "h2o_feet",
                    "tags": {"location": "coyote_creek"},
                    "fields": {"water_level": 3.0},
                    "time": 3,
                },
            ],
        )


def importFrameFromFile(pathToFile):
    tdms_frame = pre_processor.get_local_data_as_dataframe("tests/081523.tdms")
    with TdmsFile.open(path) as tdms_file:
        return tdms_file.as_dataframe()
