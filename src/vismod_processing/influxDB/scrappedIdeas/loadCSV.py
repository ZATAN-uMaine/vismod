import pandas as pd
import influxdb_client
import os
import time
from influxdb_client import InfluxDBClient, WriteOptions

import csv

# helpful little script to append annotations if I cant figure it out


def append_first_line(csv_file, line_data):
    with open(csv_file, "r", newline="") as file:
        reader = csv.reader(file)
        rows = list(reader)

    rows.insert(0, line_data)

    with open(csv_file, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(rows)


# end annotation script


organization = "zatan"

# InfluxDB URL - if on dev container use "influx:8086", if on host
# machine running docker use "localhost:8086". ("127.0.0.1:8086")
url = "http://influx:8086"
# InfluxDB Token (NEED TO LEARN HOW TO PUT THIS IN THE ENV AND REFERENCE IT)
token = os.environ.get("INFLUXDB_TOKEN")

write_client = influxdb_client.InfluxDBClient(url, token, organization)
bucket = "main"
# write_api = write_client.write_api(write_options=SYNCHRONOUS)


with InfluxDBClient.from_env_properties() as client:
    for df in pd.read_csv("test.csv", chunksize=1_000):
        with write_client.write_api() as write_api:
            try:
                write_api.write(
                    record=df,
                    bucket="dev",
                    data_frame_measurement_name="force",
                    data_frame_tag_columns=["symbol"],
                    data_frame_timestamp_column="TIME",
                )
            except InfluxDBError as e:
                print(e)

# symbol,open,high,low,close,timestamp
# vix,13.290000,13.910000,13.290000,13.570000,135935640000000000
# vix,13.870000,13.880000,13.040000,13.310000,135944280000000000
# vix,13.640000,14.330000,13.600000,14.320000,135952920000000000
#
#
# influx write -b dev \
#  -f test.csv \
#  --header "#constant measurement,force" \
#  --header "#datatype dateTime:2006-01-02,long,tag"
#
#
