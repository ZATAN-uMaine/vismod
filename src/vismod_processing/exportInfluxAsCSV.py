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


def listToString(list):

    # initialize an empty string
    string = ""

    # traverse in the string
    for ele in list:
        string += ele

    # return string
    return string


def generateFileName(start, stop):

    # Remove time-related characters from start and stop dates
    fileStartDate = start[:10]  # Extract YYYY-MM-DD from start string
    fileStopDate = stop[:10]    # Extract YYYY-MM-DD from stop string

    fileName = f"PNB_Reading_{fileStartDate}_to_{fileStopDate}.csv"

    return fileName


def querySensors(start, stop, sensors):

    print("sensors received: ")
    print(sensors)

    fileName = generateFileName(start, stop)

    exportStartTime = datetime.now()
    with InfluxDBClient(url=link, token=ourToken, org=organization)as client:
        # sensors is a list
        """ here is the full list of sensors (as of 3/3/24):
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
            '''
                from(bucket: "dev")
                |> range(start: {startTime},
                  stop: {stopTime})
                |> filter(fn: (r) => r["_measurement"] == "PNB_Reading")
                |> group(columns: [{sensorList}])
                |>pivot(rowKey:["_time"],
                         columnKey: ["_field"],
                         valueColumn: "_value")
                |> drop(columns: ["result","_start","_stop","_measurement"])
            '''
            .format(startTime=start, stopTime=stop, sensorList=sensors),
            dialect=Dialect(header=True, annotations=[], 
                            date_time_format='RFC3339', delimiter=","))

        output = csv_iterator.to_values()
        # print(output)
        # print()

        with open('test.csv', mode='w', newline='') as file:
            print("Writing to file: ", fileName)
            writer = csv.writer(file)
            # Do not write '','result', nor 'table' columns.
            for row in output:
                new_row = row[3:]  # Exclude the first three columns
                writer.writerow(new_row)

    print()
    print(f"Export finished in: {datetime.now() - exportStartTime}")
    print()
    return


def queryAllSensors(start, stop):

    fileName = generateFileName(start, stop)

    exportStartTime = datetime.now()
    with InfluxDBClient(url=link, token=ourToken, org=organization)as client:
        # Query All Sensors
        csv_iterator = client.query_api().query_csv(
            '''
                from(bucket: "dev")
                |> range(start: {startTime},
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
            '''
            .format(startTime=start, stopTime=stop),
            dialect=Dialect(header=True, annotations=[], 
                            date_time_format='RFC3339', delimiter=","))

        # Query Everything 1,000,000 minutes in the past from the dev bucket
        # csv_iterator = client.query_api().query_csv(
        #    '''from(bucket:"dev") |> range(start: -1000000m)''',
        #      dialect=Dialect(header=True, annotations=[],
        # date_time_format='RFC3339', delimiter=","))

        output = csv_iterator.to_values()
        # print(output)
        print()

        with open(fileName, mode='w', newline='') as file:
            print("Writing to file: ", fileName)
            writer = csv.writer(file)
            for row in output:
                writer.writerow(row[3:])
    print()
    print(f"Export finished in: {datetime.now() - exportStartTime}")
    print()
    return


def querySensors10AB(start, stop):

    exportStartTime = datetime.now()
    with InfluxDBClient(url=link, token=ourToken, org=organization) as client:
        # Query Sensors 10A-Left, 10A-Right, and 10A-Temp
        csv_iterator = client.query_api().query_csv(
            '''from(bucket: "dev")
                |> range(start: {startTime},
                  stop: {stopTime})
                |> filter(fn: (r) => r["_measurement"] == "PNB_Reading")
                |> group(columns: ["_measurement",
                  "10A-Left", "10A-Right", "10A-TEMP"])'''
            # |> aggregateWindow(every: 1h, fn: mean, createEmpty: false)
            # |> yield(name: "mean")'''
            .format(startTime=start, stopTime=stop),
            dialect=Dialect(header=True, annotations=[], 
                            date_time_format='RFC3339', delimiter=","))

        # Query Everything 1,000,000 minutes in the past from the dev bucket
        # csv_iterator = client.query_api().query_csv(
        #    '''from(bucket:"dev") |> range(start: -1000000m)''',
        #      dialect=Dialect(header=True, annotations=[],
        # date_time_format='RFC3339', delimiter=","))

        output = csv_iterator.to_values()
        # print(output)
        print()

        with open('test.csv', mode='w', newline='') as file:
            print("writing to file")
            writer = csv.writer(file)
            writer.writerows(output)    

    print()
    print(f"Export finished in: {datetime.now() - exportStartTime}")
    print()
    return
