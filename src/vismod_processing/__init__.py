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

    sensor_list = ["_measurement", "10A-Left", "10A-Right"]
    exportInfluxAsCSV.query_sensors('2023-08-15T04:00:00.000+04:00',
                                    '2023-08-17T00:00:00.000+04:00',
                                    sensor_list)


if __name__ == "__main__":
    main()
