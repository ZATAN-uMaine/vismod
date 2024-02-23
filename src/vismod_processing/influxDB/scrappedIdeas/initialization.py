# This script is the corrected script provided by InfluxDB for database
# initialization


import influxdb_client

# import os
import time

# from influxdb_client import InfluxDBClient
from influxdb_client import Point

# from influxdb_client import WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# InfluxDB Token (NEED TO LEARN HOW TO PUT THIS IN THE ENV AND REFERENCE IT)
# token = os.environ.get("INFLUXDB_TOKEN")
token = """EB7P3CcOXeiq46mlqnpaJWznNl97s-fwDWPG-2Y3LmRiCIbqcXmBlTu1-YrWQvVBtfZBxCQI1j_pBP6laoFY2Q=="""

# InfluxDB Organization
organization = "zatan"

# InfluxDB URL - if on dev container use "influx:8086", if on host
# machine running docker use "localhost:8086". ("127.0.0.1:8086")
url = "http://influx:8086"


write_client = influxdb_client.InfluxDBClient(url, token, organization)
bucket = "main"
write_api = write_client.write_api(write_options=SYNCHRONOUS)
for value in range(5):
    point = (
        Point("force")  # point is going to be the thing being measured
        .tag("Node", value)
        .field("pounds", 10000 * value)
    )
    write_api.write(bucket=bucket, org="zatan", record=point)
    time.sleep(1)

bucket = "main"
write_api = write_client.write_api(write_options=SYNCHRONOUS)
for value in range(5):
    point = (
        Point("temperature")
        .tag("tempSensor", value)
        .field("degreesF", 10 * value)
    )
    write_api.write(bucket=bucket, org="zatan", record=point)
    time.sleep(1)

bucket = "main"
write_api = write_client.write_api(write_options=SYNCHRONOUS)
for value in range(1):
    point = (
        Point("windDirection")
        .tag("windSensor", value)
        .field("degrees", 30 * value)
    )
    write_api.write(bucket=bucket, org="zatan", record=point)
    time.sleep(1)

bucket = "main"
write_api = write_client.write_api(write_options=SYNCHRONOUS)
for value in range(1):
    point = (
        Point("windSpeed")
        .tag("windSensor", value)
        .field("feet/second", value * 70)
    )

    write_api.write(bucket=bucket, org="zatan", record=point)
    time.sleep(1)

query_api = write_client.query_api()

query = """from(bucket: "main")
 |> range(start: -10m)
 |> filter(fn: (r) => r._measurement == "force")"""
tables = query_api.query(query, org="zatan")

for table in tables:
    for record in table.records:
        print(record)


query = """from(bucket: "main")
  |> range(start: -10m)
  |> filter(fn: (r) => r._measurement == "force")
  |> mean()"""
tables = query_api.query(query, org="zatan")

for table in tables:
    for record in table.records:
        print(record)
