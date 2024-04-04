from dotenv import load_dotenv
import sys
import logging

from vismod_processing import pre_processing
from vismod_processing import importDataFromPandas
from vismod_processing import config_fetch
from vismod_processing import data_fetch


def main():
    """Main function to run the data processing pipeline"""
    load_dotenv()

    # Enable logging
    handler = logging.basicConfig(level=logging.DEBUG, force=True)
    # capture logs from Influx dataframe_serializer module
    logger_serializer = logging.getLogger(
        "influxdb_client.client.write.dataframe_serializer"
    )
    logger_serializer.setLevel(level=logging.DEBUG)
    # handler.setFormatter(logging.Formatter("%(asctime)s | %(message)s"))
    logger_serializer.addHandler(handler)

    target_file = None
    if len(sys.argv) == 2:
        target_file = sys.argv[1]
        logging.info(f"Running with specific TDMS file {target_file}")

    data_files = data_fetch.tdmsDownload(target_file=target_file)

    if len(data_files) == 0:
        logging.info("No new data files")
        return

    # download the config from drive
    config = config_fetch.download_config()
    logging.debug(config)
    proc = pre_processing.Pre_Processor(config)

    for df in data_files:
        data = proc.load_and_process(df)
        if data is None:
            continue

        # sensor list for exporting script
        # call upload script
        frames = importDataFromPandas.df_to_influx_format(data)
        for frame in frames:
            logging.info(frame.head())
            logging.info(frame.columns)
            importDataFromPandas.upload_data_frame(frame)

    # Clean up tmp files
    data_fetch.cleanTmpFiles()


if __name__ == "__main__":
    main()
