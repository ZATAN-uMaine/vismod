import os
import csv
import logging
from datetime import datetime
from pathlib import Path
from influxdb_client import InfluxDBClient, Dialect


# Load database secrets
ourToken = os.environ.get("INFLUXDB_V2_TOKEN")
organization = os.environ.get("INFLUXDB_V2_ORG")
link = os.environ.get("INFLUXDB_V2_URL")
zatan_bucket = os.environ.get("INFLUXDB_V2_BUCKET")

# default values for querying -- these get pruned for specific requests
STRAIN_SENSORS = [  # easier  to add sensors with comprehension (?)
    sensor
    for x in ["2", "10", "17"]
    for sensor in (x + "A-Left", x + "A-Right", x + "B-Left", x + "B-Right")
]
AUXILIARY_SENSORS = [
    "External-Temperature",
    "External-Wind-Direction",
    "External-Wind-Speed",
]
ALL_SENSORS = STRAIN_SENSORS + AUXILIARY_SENSORS

STRAIN_UNITS = {  # every stay gets the same unit
    key: "strain (lbs)" for key in STRAIN_SENSORS
}
AUXILIARY_UNITS = {
    "_time": "",
    "External-Temperature": "degrees (F)",
    "External-Wind-Direction": "angle (degrees)",
    "External-Wind-Speed": "feet/second",
}
ALL_UNITS = {**STRAIN_UNITS, **AUXILIARY_UNITS}
CSV_TMP_PATH = "/tmp"


def list_to_string(list):
    """
    This method converts a list to a string in Python.
    It takes a list as input.
    """
    # initialize an empty string
    string = ""

    # traverse in the string
    for ele in list:
        string += ele

    # return string
    return string


def generate_file_name(start, stop):
    """
    This method generates the file name for the output file
    It takes a start time and a stop time as input.
    The format for these times is RFC3339.
    """
    # Remove time-related characters from start and stop dates
    fileStartDate = start[:10]  # Extract YYYY-MM-DD from start string
    fileStopDate = stop[:10]  # Extract YYYY-MM-DD from stop string
    now = datetime.now()
    time_since_midnight = now - now.replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    stamp = round(time_since_midnight.total_seconds() * 1000)
    file_name = f"PNB_Reading_{fileStartDate}_to_{fileStopDate}_{stamp}.csv"

    return file_name


def format_sensor_list(sensors):
    """
    This method takes the list of sensors as input
    and outputs them into a formatted query string
    to be injected into the query.
    """
    # require that the passed sensors match pre-determined sensors
    received_sensors = [sensor for sensor in sensors if sensor in ALL_SENSORS]
    logging.debug(f"Valid sensors received: {received_sensors}")

    for index, item in enumerate(received_sensors):
        if index == 0:
            received_sensors[index] = 'r["node"] == "' + item + '"'
        else:
            received_sensors[index] = ' or r["node"] == "' + item + '"'
    partially_formatted_sensors = list_to_string(received_sensors)
    logging.debug(
        f"partial format applied: {repr(partially_formatted_sensors)}"
    )
    formatted_sensors = partially_formatted_sensors.replace('"', '"')
    return formatted_sensors


def query_sensors(start, stop, sensors):
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
    parent = Path(CSV_TMP_PATH)
    csv_path = generate_file_name(start, stop)
    write_to = parent / csv_path
    formatted_sensors = format_sensor_list(sensors)

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
                |> filter(fn: (r) => r["_measurement"] == "NodeStrain")
                |> filter(fn: (r) => r["_field"] == "_value")
                |> filter(fn: (r) => {sensor_list})
                |>pivot(rowKey:["_time"],
                         columnKey: ["node"],
                         valueColumn: "_value")
                |> group()
                |> drop(columns:
                    ["result","_start","_stop","_measurement","_field"])
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
        logging.info(f"Found {len(output)} rows to export")

        with open(write_to, mode="w", newline="") as file:
            writer = csv.writer(file)

            header_row = output[0][3:]
            writer.writerow(header_row)

            units = [ALL_UNITS[column] for column in header_row]
            writer.writerow(units)

            for row in output[1:]:  # the rest of the output
                writer.writerow(row[3:])

    logging.info(f"Export finished in: {datetime.now() - export_start_time}")
    return write_to


def query_all_sensors(start, stop):
    """
    This method is used to query all sensors
    It takes a start time and a stop time as input.
    The format for these times is RFC3339.
    (currently using standard est, daylight savings would be +05:00)
    example:
    exportInfluxAsCSV.query_all_sensors(
        '2023-08-15T04:00:00.000+04:00', '2023-08-17T00:00:00.000+04:00')
    """
    parent = Path(CSV_TMP_PATH)
    csv_path = generate_file_name(start, stop)
    write_to = parent / csv_path
    logging.info(f"exporting data from all sensors to {write_to}")
    formatted_sensors = format_sensor_list(ALL_SENSORS)

    export_start_time = datetime.now()
    with InfluxDBClient(url=link, token=ourToken, org=organization) as client:
        # Query All Sensors
        csv_iterator = client.query_api().query_csv(
            """
                from(bucket: "{bucket_name}")
                |> range(start: {start_time},
                  stop: {stopTime})
                |> filter(fn: (r) => r["_measurement"] == "NodeStrain")
                |> filter(fn: (r) => r["_field"] == "_value")
                |> filter(fn: (r) => {sensor_list})
                |>pivot(rowKey:["_time"],
                         columnKey: ["node"],
                         valueColumn: "_value")
                |> group()
                |> drop(columns:
                        ["result","_start","_stop","_measurement","_field"])
            """.format(
                bucket_name=str(zatan_bucket),
                start_time=start,
                stopTime=stop,
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
        logging.info(f"Found {len(output)} rows to export")

        with open(write_to, mode="w", newline="") as file:
            writer = csv.writer(file)

            header_row = output[0][3:]
            writer.writerow(header_row)

            units = [ALL_UNITS[column] for column in header_row]
            writer.writerow(units)

            for row in output[1:]:  # the rest of the output
                writer.writerow(row[3:])
    logging.info(f"Export finished in: {datetime.now() - export_start_time}")
    return write_to


def string_process(st):
    return st * 2


'''
def query_sensors_10AB(start, stop):
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
'''
