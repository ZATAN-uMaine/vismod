from vismod_processing import pre_processing
from vismod_processing import importDataFromPandas
from vismod_processing import exportInfluxAsCSV
import json


def main():
    config = json.load(open("tests/data/example-config.json"))
    proc = pre_processing.Pre_Processor(config)
    data = proc.load_and_process("tests/data/081523.tdms")
    print(data.head())
    print(data.columns)

    # call upload script
    importDataFromPandas.upload_data_frame(data, "dev")

    # query each sensor (currently using standard est,
    # daylight savings would be +05:00)
    # exportInfluxAsCSV.queryAllSensors('2023-08-15T04:00:00.000+04:00',
    #                                  '2023-08-17T00:00:00.000+04:00')

    # query node 10 with sensors 10A, 10B, and Temp (UTC/GMT)
    # exportInfluxAsCSV.querySensors10AB('2023-08-16T00:00:00.000Z', 
    # '2023-08-17T00:00:00.000Z')

    # Parameterized query for sensors
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
    # to query your sensor follow the following format (EST):
    # exportInfluxAsCSV.querySensors(
    # 'YYYY-MM-DDT00:00:00.000+04:00',
    # 'YYYY-MM-DDT00:00:00.000+04:00',
    # [<sensorlist>])
    # INCLUDE "_measurement" as an item in sensor list!!!

    sensor_list = ["_measurement","10A-Left", "10A-Right"]
    exportInfluxAsCSV.query_sensors('2023-08-15T04:00:00.000+04:00',
                                  '2023-08-17T00:00:00.000+04:00',
                                    sensor_list)


if __name__ == "__main__":
    main()
