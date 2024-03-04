from dotenv import load_dotenv

from vismod_processing import pre_processing
from vismod_processing import importDataFromPandas
from vismod_processing import config_fetch
from vismod_processing import data_fetch


def main():
    load_dotenv()

    data_files = data_fetch.tdmsDownload()
    print(data_files)

    # download the config from drive
    config = config_fetch.download_config()
    print(config)
    proc = pre_processing.Pre_Processor(config)

    for df in data_files:
        data = proc.load_and_process(df)
        print(data.head())
        print(data.columns)

        # call upload script
        importDataFromPandas.uploadDataFrame(data, "dev")


if __name__ == "__main__":
    main()
