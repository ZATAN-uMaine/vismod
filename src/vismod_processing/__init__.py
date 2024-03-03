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
    importDataFromPandas.uploadDataFrame(data, "dev")
    
    # query each sensor
    #exportInfluxAsCSV.queryAllSensors('2022-01-01T00:00:00Z', '2024-03-02T11:11:11Z')
    
    # query node 10 with sensors 10A, 10B, and Temp
    exportInfluxAsCSV.queryAllSensors('2022-01-01T00:00:00Z', '2024-03-02T11:11:11Z')


if __name__ == "__main__":
    main()
