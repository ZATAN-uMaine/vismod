from os import environ
import logging

from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS


class VismodInfluxClient:
    def __init__(self, client: InfluxDBClient):
        self.client: InfluxDBClient = client

    def write(self):
        return self.client.write_api(write_options=SYNCHRONOUS)

    def write_row(self, tags, fields, time, measurement):
        record = {
            "time": time,
            "measurement": measurement,
            "tags": tags,
            "fields": fields,
        }
        writer = self.write()
        writer.write(bucket=self.bucket(), record=record)
        writer.close()

    def read_last_with_tag(self, measurement, tag_name, tag_value):
        """
        Reads the most recent `measurement` that has a `tag_name`
        with the value `tag_value`. Returns None if it cannot be found.
        """
        results = self.client.query_api().query(
            f"""
              from(bucket: "{self.bucket()}")
              |> range(start: 0)
              |> filter(fn: (r) => r["_measurement"] == "{measurement}")
              |> filter(fn: (r) => r["{tag_name}"] == "{tag_value}")
              |> group()
              |> last()
            """
        )
        if len(results) != 1:
            return None
        row = results[0]
        return row.records[0].values

    def bucket(self):
        bucket = environ.get("INFLUXDB_V2_BUCKET")
        if bucket is None:
            logging.warn("could not find $INFLUXDB_V2_BUCKET")
            raise Exception("missing env vars")
        return bucket


class VismodInfluxBuilder:
    def __init__(self):
        self.zatan_token = environ.get("INFLUXDB_V2_TOKEN")
        self.organization = environ.get("INFLUXDB_V2_ORG")
        self.link = environ.get("INFLUXDB_V2_URL")
        self.zatan_bucket = environ.get("INFLUXDB_V2_BUCKET")

        if (
            self.link is None
            or self.zatan_bucket is None
            or self.organization is None
            or self.zatan_token is None
        ):
            logging.warning("Missing env vars for Influx connection")
            raise Exception("Missing env vars")

    def __enter__(self):
        client = InfluxDBClient(
            url=self.link, token=self.zatan_token, org=self.organization
        )
        client.health()
        self.client = client
        return VismodInfluxClient(self.client)

    def __exit__(self, exception_type, exception_value, _traceback):
        if exception_value is not None:
            logging.warn("influx connection failed: ", exception_type)
        self.client.close()
