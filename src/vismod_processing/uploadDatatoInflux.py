from dotenv import load_dotenv
from influxdb_client import InfluxDBClient, Point, WriteOptions
from influxdb_client.client.write_api import SYNCHRONOUS



    """Example to read JSON data and send to InfluxDB."""


    load_dotenv(dotenv_path=Path(".env"))


point = Point("Calib_Table")
with open("data.json", "r") as json_file:
    data = json.load(json_file)
    point.tag("node1", data["43641"])
    point.tag("node2", data["43641"])
    point.tag("node3", data["43644"])
    point.tag("node", data["43642"])
    point.tag("node", data["45616"])
    point.tag("node", data["43643"])
    point.tag("node", data["45617"])
    point.tag("channel", data["1","2"])
    for key, value in data["1"].items():
        point.field(key, value)
    for key, value in data["2"].items():
        point.field(key, value)


with InfluxDBClient.from_env_properties() as client:
    # use the client to access the necessary APIs
    # for example, write data using the write_api
    with client.write_api() as writer:
        writer.write(bucket="dev", record=point)



# # Convert dictionaries to InfluxDB JSON format
# influxdb_data = []
# for node, channels in nested_dictionaries.items():
#     for channel, data in channels.items():
#         influxdb_data.append({


# # Write data to InfluxDB
# client.write_points(influxdb_data)