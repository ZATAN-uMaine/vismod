from dotenv import load_dotenv
import logging
import influxdb_client
import click
import re
from os.path import exists

from vismod_processing import pre_processing
from vismod_processing import importDataFromPandas
from vismod_processing import config_fetch
from vismod_processing import data_fetch


def validate_local_files(ctx, param, value):
    """
    Checks to make sure that the provided arguments are local
    files that actually exist.
    """
    if value is None:
        return value
    if isinstance(value, tuple):
        for path in value:
            if not (exists(path)):
                raise click.BadParameter(f"{path} could not be opened.")
        return value
    raise click.BadParameter("filename must be a string")


def validate_name(ctx, param, value):
    """
    Checks to make sure the provided argument is a list of valid
    TDMS names.
    """
    if value is None:
        return value
    file_name_regex = re.compile("^.*\\.tdms$")
    if isinstance(value, tuple):
        for name in value:
            if not (file_name_regex.match(name)):
                raise click.BadParameter(
                    f"'{value}' does not appear to be a valid .tdms file name."
                )
        return value
    raise click.BadParameter("filename must be a string")


@click.command()
@click.option(
    "drive_files",
    "--drive-file",
    type=click.UNPROCESSED,
    callback=validate_name,
    multiple=True,
    help="The names of TDMS files in the Google Drive to download, process, and import.",  # noqa
)
@click.option(
    "local_files",
    "--local-file",
    type=click.Path(),
    callback=validate_local_files,
    multiple=True,
    help="The names of local TDMS files to process and import.",  # noqa
)
@click.option(
    "save_as",
    "--save-to-file",
    type=click.Path(),
    help="Save as local CSV file instead of importing to influx.",
)
@click.option(
    "download_count",
    "--drive-download-count",
    default=1,
    help="How many TDMS files to attempt to download (in reverse order from most recent).",  # noqa
)
def main(drive_files, local_files, save_as, download_count):
    """Main function to run the data processing pipeline"""
    load_dotenv()

    # Enable logging
    handler = logging.basicConfig(level=logging.DEBUG, force=True)
    # capture logs from Influx dataframe_serializer module
    logger_serializer = logging.getLogger(
        "influxdb_client.client.write.dataframe_serializer"
    )
    logger_serializer.setLevel(level=logging.DEBUG)
    logger_serializer.addHandler(handler)

    # download the config from drive
    config = config_fetch.download_config()
    logging.debug(config)
    proc = pre_processing.Pre_Processor(config)

    # download data files
    data_files = []
    if len(drive_files) > 0:
        logging.info("Downloading specified files from drive")
        for target_file in drive_files:
            dfs = data_fetch.tdmsDownload(target_file=target_file)
            data_files.extend(dfs)

    if len(local_files) > 0:
        data_files.extend(local_files)

    if len(drive_files) + len(local_files) == 0:
        data_files.extend(
            data_fetch.tdmsDownload(target_file=None, count=download_count)
        )

    if len(data_files) == 0:
        logging.info("No new data files")
        return

    # process data
    processed_frames = []
    for df in data_files:
        logging.info(f"processing tdms file {df}")
        data = proc.load_and_process(df)
        if data is None:
            continue
        processed_frames.append(data)

    # export data
    if save_as is not None:
        logging.info(f"Saving data to files {save_as}.*")
        logging.info("WILL NOT EXPORT TO INFLUX")
        for index, data in enumerate(processed_frames):
            data.to_csv(f"{save_as}.{index}")
    else:
        for data in processed_frames:
            # sensor list for exporting script
            # call upload script
            frames = importDataFromPandas.df_to_influx_format(data)
            for frame in frames:
                try:
                    importDataFromPandas.upload_data_frame(frame)
                except influxdb_client.rest.ApiException as err:
                    logging.error(err)

    # Clean up tmp files
    data_fetch.clean_tmp_files()


if __name__ == "__main__":
    main()
