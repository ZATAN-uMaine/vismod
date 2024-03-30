from dotenv import load_dotenv
import sys

from vismod_processing import pre_processing
from vismod_processing import importDataFromPandas
from vismod_processing import config_fetch
from vismod_processing import data_fetch


def main():
    """Main function to run the data processing pipeline"""
    load_dotenv()

    target_file = None
    if len(sys.argv) == 2:
        target_file = sys.argv[1]
        print(f"Running with specific TDMS file {target_file}")

    data_files = data_fetch.tdmsDownload(target_file=target_file)
    print(data_files)

    if len(data_files) == 0:
        print("No new data files")
        return

    # download the config from drive
    config = config_fetch.download_config()
    print(config)
    proc = pre_processing.Pre_Processor(config)

    for df in data_files:
        data = proc.load_and_process(df)
        if data is None:
            continue

        # sensor list for exporting script
        # call upload script
        frames = importDataFromPandas.df_to_influx_format(data)
        for frame in frames:
            print(frame.head())
            print(frame.columns)
            importDataFromPandas.upload_data_frame(frame)

    # Clean up tmp files
    data_fetch.cleanTmpFiles()


if __name__ == "__main__":
    main()
