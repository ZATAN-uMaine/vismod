import pandas as pd
import os
import json
from influxdb_client import Point, InfluxDBClient, WriteOptions  




def process_excel_to_dict(excel_file):
    # Read the Excel file
    df = pd.read_excel(excel_file, header=2)  # Column headers start at row 3

    # Extract contact info from Column A, skip unpopulated
    contact_info = df.iloc[4:, 0].dropna().tolist()

    # TODO move this to DB # Save contact info to a text file
    with open("contactinfo.txt", "w") as file:
        for info in contact_info:
            file.write(f"{info}\n")

    # Prepare dictionaries
    nested_dictionaries = {}
    for _, row in df.iloc[1:].iterrows():
        if pd.notna(row["Node"]):  # Check if column 'Node' is populated
            node = str(row["Node"])
            if node not in nested_dictionaries:
                nested_dictionaries[node] = {}  # Initialize a new dictionary

            dict_entry = {
                # Load cell calibration factor
                "Cal_Factor": row["Cal Factor_L"],
                # Cable ID is the label, row['Cable ID'] is the value
                "Cable ID": row["Cable ID"],
                # Since the TDMS files also use 'TEMP'
                # we will also use it here for consistency
                "TEMP": row["Cal Factor_T"],
            }

            # WDAQ channel number as key, 'Cal Factor' as value
            nested_dictionaries[node][row["WDAQ_L"]] = dict_entry

    # Convert dictionaries to JSON
    json_data = json.dumps(nested_dictionaries)

    # TODO move this to DB
    # Write JSON data to file
    with open("data.json", "w") as file:
        file.write(json_data)

    return nested_dictionaries


if __name__ == "__main__":
    # Adjust the path to the Excel file as necessary
    excel_file_path = "config.xlsx"

excel_file_path = "config.xlsx"
nested_dictionaries = process_excel_to_dict(excel_file_path)
# print(nested_dictionaries)
# Convert dictionaries to JSON
json_data = json.dumps(nested_dictionaries)

# TODO move this to DB
# Write JSON data to file
with open("data.json", "w") as file:
    file.write(json_data)


#!/usr/bin/env python3
    """Example to read JSON data and send to InfluxDB."""

from dateutil import parser
import json

from influxdb_client import InfluxDBClient, Point, WriteOptions
from influxdb_client.client.write_api import SYNCHRONOUS


point = Point("Calib_Table")

data = json_data

point = Point("Calib_Table")
with open("data.json", "r") as json_file:
    data = json.load(json_file)
    point.tag("node", data["43641","43644","43642","45616","43643","45617"])
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