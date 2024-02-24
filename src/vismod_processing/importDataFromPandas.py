import pandas as pd
import os
import logging
import random
from datetime import datetime
from nptdms import TdmsFile
from dotenv import load_dotenv
from influxdb_client import Point, InfluxDBClient, WriteOptions  
from influxdb_client.client.write_api import SYNCHRONOUS, PointSettings
from influxdb_client.extras import pd, np

# Import ZATAN's Pre Processor Class
import pre_processing

# Load environment
load_dotenv(dotenv_path=Path(".env"))


# Enable logging for DataFrame serializer

loggerSerializer = logging.getLogger('influxdb_client.client.write.dataframe_serializer')
loggerSerializer.setLevel(level=logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s | %(message)s'))
loggerSerializer.addHandler(handler)

# Load database secrets
zatanToken = os.environ.get("INFLUXDB_V2_TOKEN")
organization = os.environ.get("INFLUXDB_V2_ORG")
link = os.environ.get("INFLUXDB_V2_URL")

bucket = "dev"

# set paths for necessary files
pathToFile = "../../tests/081523.tdms"
calibTablePath = '/raw-DAQ-files/sensorCalib.xlsx'

print("initializing processor")
# Creating a Pre_Processor instance
processor = pre_processing.Pre_Processor("../../tests/config.xlsx")
print("initialized processor")
print("\n Printint calib table")
print(processor.calib_table)
print("\n")

# Initialize data frame
dataFrame = processor.get_local_data_as_dataframe(pathToFile)
print("initialized Dataframe")


def multiplier(item, table, sensor, channel):
    return 70 - (item * table[sensor][channel])


print("MADE IT TO DATA PROCESSOR")
tdmsDict = processor.apply_calibration(
   dataFrame, fun=multiplier
)
print("ESCAPED DATA PROCESSOR")
print(tdmsDict)
# End data frame initialization

# Initialize Database Client
print()
print("=== Ingesting DataFrame via batching API ===")
print()
startTime = datetime.now()
with InfluxDBClient(url=link, token=zatanToken, org=organization) as client:

    # Use batching API
    with client.write_api() as write_api:
        write_api.write(bucket=bucket, record=dataFrame,
                        data_frame_tag_columns=['tag'],
                        data_frame_measurement_name="measurement_name")
        print()
        print("Wait to finishing ingesting DataFrame...")
        print()

print()
print(f'Import finished in: {datetime.now() - startTime}')
print()


# Generate Dataframe
# """
# print()
# print("=== Generating DataFrame ===")
# print()
# dataframe_rows_count = 150_000

# col_data = {
#     'time': np.arange(0, dataframe_rows_count, 1, dtype=int),
#     'tag': np.random.choice(['tag_a', 'tag_b', 'test_c'], size=(dataframe_rows_count,)),
# }
# for n in range(2, 2999):
#     col_data[f'col{n}'] = random.randint(1, 10)

# data_frame = pd.DataFrame(data=col_data).set_index('time')
# print(data_frame)

"""
Ingest DataFrame
"""
