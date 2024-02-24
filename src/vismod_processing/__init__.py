from vismod_processing import pre_processing
import json


def main():
    config = json.load(open("tests/data/example-config.json"))
    proc = pre_processing.Pre_Processor(config)
    data = proc.load_and_process("tests/081523.tdms")
    print(data.shape)
    print(data.head())


if __name__ == "__main__":
    main()
