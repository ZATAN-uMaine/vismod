from os import environ
import logging

from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS


class VismodInfluxClient:
    def __init__(self, client: InfluxDBClient):
        self.client = client

    def write(self):
        return self.cli.write_api(write_options=SYNCHRONOUS)


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
            url=self.link, token=self.zatan_token, org=self.zatan_bucket
        )
        client.health()
        return VismodInfluxClient(client)

    def __exit__(self, exception_type, exception_value, _traceback):
        logging.warn("influx connection failed", exception_value)
