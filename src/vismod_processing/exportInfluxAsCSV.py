import os
import csv
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
from influxdb_client import InfluxDBClient, Dialect

# Load environment
load_dotenv(dotenv_path=Path(".env"))


# Load database secrets
ourToken = os.environ.get("INFLUXDB_V2_TOKEN")
organization = os.environ.get("INFLUXDB_V2_ORG")
link = os.environ.get("INFLUXDB_V2_URL")
zatan_bucket = os.environ.get("INFLUXDB_V2_BUCKET")

"""
This method converts a list to a string in Python.
It takes a list as input.
"""


def list_to_string(list):

    # initialize an empty string
    string = ""

    # traverse in the string
    for ele in list:
        string += ele

    # return string
    return string


"""
This method generates the file name for the output file
It takes a start time and a stop time as input.
The format for these times is RFC3339.
"""


def generate_file_name(start, stop):

    # Remove time-related characters from start and stop dates
    fileStartDate = start[:10]  # Extract YYYY-MM-DD from start string
    fileStopDate = stop[:10]  # Extract YYYY-MM-DD from stop string

    file_name = f"PNB_Reading_{fileStartDate}_to_{fileStopDate}.csv"

    return file_name


"""
This method takes the list of sensors as input
and outputs them into a formatted query string
to be injected into the query.
"""


def format_sensor_list(sensors):
    received_sensors = sensors
    print("sensors received: ")
    print(received_sensors)

    for index, item in enumerate(received_sensors):
        if index == 0:
            received_sensors[index] = 'r["_field"] == "' + item + '"'
        else:
            received_sensors[index] = ' or r["_field"] == "' + item + '"'
    partially_formatted_sensors = list_to_string(received_sensors)
    print("partial format applied: ")
    print(repr(partially_formatted_sensors))
    formatted_sensors = partially_formatted_sensors.replace('"', '"')
    return formatted_sensors


"""
query_sensors is our custom and most up to date
querying method. It takes a start time, stop time,
and a list of desired sensors as input.


    # Parameterized query for sensors
    # sensors is a list
    here is the full list of sensors (as of 3/3/24):
                ["_measurement",
                "10A-Left", "10A-Right", "10A-TEMP",
                "10B-Left", "10B-Right", "10B-TEMP",
                "17A-Left", "17A-Right", "17A-TEMP",
                "17B-Left", "17B-Right", "17B-TEMP",
                "2A-Left", "2A-Right", "2A-TEMP",
                "2B-Left", "2B-Right", "2B-TEMP",
                "External-Temperature",
                "External-Wind-Direction",
                "External-Wind-Speed"]
    # to query your sensor follow the following format (EST):
    # exportInfluxAsCSV.querySensors(
    # 'YYYY-MM-DDT00:00:00.000+04:00',
    # 'YYYY-MM-DDT00:00:00.000+04:00',
    # [<sensorlist>])
    # INCLUDE "_measurement" as an item in sensor list!!!
"""


def query_sensors(start, stop, sensors):

    formatted_sensors = format_sensor_list(sensors)

    # Generate the file name for the output file
    file_name = generate_file_name(start, stop)

    export_start_time = datetime.now()
    with InfluxDBClient(url=link, token=ourToken, org=organization) as client:
        # sensors is a list
        """here is the full list of sensors (as of 3/3/24):
        ["_measurement",
         "10A-Left", "10A-Right", "10A-TEMP",
         "10B-Left", "10B-Right", "10B-TEMP",
         "17A-Left", "17A-Right", "17A-TEMP",
         "17B-Left", "17B-Right", "17B-TEMP",
         "2A-Left", "2A-Right", "2A-TEMP",
         "2B-Left", "2B-Right", "2B-TEMP",
         "External-Temperature",
         "External-Wind-Direction",
         "External-Wind-Speed"]
        """
        csv_iterator = client.query_api().query_csv(
            """
                from(bucket: "{bucket_name}")
                |> range(start: {start_time},
                  stop: {stop_time})
                |> filter(fn: (r) => r["_measurement"] == "PNB_Reading")
                |> filter(fn: (r) => {sensor_list})
                |>pivot(rowKey:["_time"],
                         columnKey: ["_field"],
                         valueColumn: "_value")
                |> drop(columns: ["result","_start","_stop","_measurement"])
            """.format(
                bucket_name=str(zatan_bucket),
                start_time=start,
                stop_time=stop,
                sensor_list=formatted_sensors,
            ),
            dialect=Dialect(
                header=True,
                annotations=[],
                date_time_format="RFC3339",
                delimiter=",",
            ),
        )
        output = csv_iterator.to_values()
        print("here is our output")
        print(output)
        print()

        with open(file_name, mode="w", newline="") as file:
            print("Writing to file: ", file_name)
            writer = csv.writer(file)
            # Do not write '','result', nor 'table' columns.
            for row in output:
                new_row = row[3:]  # Exclude the first three columns
                # print(row)
                writer.writerow(new_row)

    print()
    print(f"Export finished in: {datetime.now() - export_start_time}")
    print()

    print()
    print(f"Export finished in: {datetime.now() - export_start_time}")
    print()
    return file_name


"""
This method is used to query all sensors
It takes a start time and a stop time as input.
The format for these times is RFC3339.
(currently using standard est, daylight savings would be +05:00)
example:
exportInfluxAsCSV.query_all_sensors(
    '2023-08-15T04:00:00.000+04:00', '2023-08-17T00:00:00.000+04:00')
"""


def query_all_sensors(start, stop):
    parent = Path("src/vismod_web/")
    csv_path = Path("user_csvs") / generate_file_name(start, stop)
    write_to = parent / csv_path

    export_start_time = datetime.now()
    with InfluxDBClient(url=link, token=ourToken, org=organization) as client:
        # Query All Sensors
        csv_iterator = client.query_api().query_csv(
            """
                from(bucket: "{bucket_name}")
                |> range(start: {start_time},
                  stop: {stopTime})
                |> filter(fn: (r) => r["_measurement"] == "PNB_Reading")
                |> group(columns: ["_measurement",
                  "10A-Left", "10A-Right", "10A-TEMP",
                  "10B-Left", "10B-Right", "10B-TEMP",
                  "17A-Left", "17A-Right", "17A-TEMP",
                  "17B-Left", "17B-Right", "17B-TEMP",
                  "2A-Left", "2A-Right", "2A-TEMP",
                  "2B-Left", "2B-Right", "2B-TEMP",
                  "External-Temperature",
                  "External-Wind-Direction",
                  "External-Wind-Speed"])
                |>pivot(rowKey:["_time"],
                         columnKey: ["_field"],
                         valueColumn: "_value")
                |> drop(columns: ["result","_start","_stop","_measurement"])
            """.format(
                bucket_name=str(zatan_bucket), start_time=start, stopTime=stop
            ),
            dialect=Dialect(
                header=True,
                annotations=[],
                date_time_format="RFC3339",
                delimiter=",",
            ),
        )

        output = csv_iterator.to_values()
        # print(output)
        print()

        with open(write_to, mode="w", newline="") as file:
            print("Writing to file: ", csv_path)
            writer = csv.writer(file)
            for row in output:
                writer.writerow(row[3:])
    print()
    print(f"Export finished in: {datetime.now() - export_start_time}")
    print()
    return csv_path


"""
This is the first successful query we wrote, and if needed can serve as
a template method for querying each sensor individually.
It takes a start time and a stop time as input.
The format for these times is RFC3339.
This method specifically queries node 10 with sensors 10A, 10B,
 and Temp (UTC/GMT). Please see query_all_sensors for EST.
example: exportInfluxAsCSV.query_sensors_10AB(
    '2023-08-16T00:00:00.000Z', '2023-08-17T00:00:00.000Z')
For EST please see query_all_sensors.
"""


def query_sensors_10AB(start, stop):

    export_start_time = datetime.now()
    with InfluxDBClient(url=link, token=ourToken, org=organization) as client:
        # Query Sensors 10A-Left, 10A-Right, and 10A-Temp
        csv_iterator = client.query_api().query_csv(
            """from(bucket: "{bucket_name}")
                |> range(start: {start_time},
                  stop: {stopTime})
                |> filter(fn: (r) => r["_measurement"] == "PNB_Reading")
                |> group(columns: ["_measurement",
                  "10A-Left", "10A-Right", "10A-TEMP"])""".format(
                bucket_name=str(zatan_bucket), start_time=start, stopTime=stop
            ),
            dialect=Dialect(
                header=True,
                annotations=[],
                date_time_format="RFC3339",
                delimiter=",",
            ),
        )

        output = csv_iterator.to_values()
        # print(output)
        print()

        with open("test.csv", mode="w", newline="") as file:
            print("writing to file")
            writer = csv.writer(file)
            writer.writerows(output)

    print()
    print(f"Export finished in: {datetime.now() - export_start_time}")
    print()
    return


def string_process(st):
    return st*2


def generate_csv():
    # Example: Generate CSV content
    csv_data = [
        ['Name', 'Age', 'City'],
        ['John', 30, 'New York'],
        ['Alice', 25, 'London'],
        ['Bob', 35, 'Paris']
    ]

    return csv_data