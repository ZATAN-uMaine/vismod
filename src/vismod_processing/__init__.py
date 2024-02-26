from vismod_processing import pre_processing
from vismod_processing import importDataFromPandas
import json


def main():
    config = json.load(open("tests/data/example-config.json"))
    proc = pre_processing.Pre_Processor(config)
    data = proc.load_and_process("tests/data/081523.tdms")
    print(data.head())
    print(data.columns)

    # call upload script
    importDataFromPandas.uploadDataFrame(data, "dev")


if __name__ == "__main__":
    main()
