import pandas as pd
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
from influxdb_client import InfluxDBClient   
from influxdb_client.extras import pd, np

# Import ZATAN's Pre Processor Class
import pre_processing

# Load environment
load_dotenv(dotenv_path=Path(".env"))


# Enable logging for DataFrame serializer

loggerSerializer = logging.getLogger(
    'influxdb_client.client.write.dataframe_serializer'
    )
loggerSerializer.setLevel(level=logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s | %(message)s'))
loggerSerializer.addHandler(handler)

# Load database secrets
zatanToken = os.environ.get("INFLUXDB_V2_TOKEN")
organization = os.environ.get("INFLUXDB_V2_ORG")
link = os.environ.get("INFLUXDB_V2_URL")

# set paths for necessary files
pathToFile = "../../tests/081523.tdms"
calibTablePath = '/raw-DAQ-files/sensorCalib.xlsx'


def uploadDataFrame(df, bucket):
# Initialize data frame
    dataFrame = df
    bucket = bucket

    # Initialize Database Client
    print()
    print("=== Ingesting DataFrame via batching API ===")
    print()
    startTime = datetime.now()
    with InfluxDBClient(url=link, token=zatanToken, org=organization) as client:

        # Use batching API
        with client.write_api() as write_api:
            write_api.write(bucket=bucket, record=dataFrame,
                            data_frame_tag_columns=['17A-TEMP', '17A-Left',
                                '17A-Right', '10A-TEMP', '10A-TIME', '10A-Left',
                                '10A-Right', '2A-TEMP', '2A-TIME', '2A-Left', 
                                '2A-Right', '2B-TEMP', '2B-TIME', '2B-Left', 
                                '2B-Right', '10B-TEMP', '10B-TIME', '10B-Left',
                                '10B-Right', '17B-TEMP', '17B-TIME', '17B-Left',
                                '17B-Right'],
                            data_frame_measurement_name="PNB_Reading",)
                            
            print()
            print("Wait to finishing ingesting DataFrame...")
            print()

    print()
    print(f'Import finished in: {datetime.now() - startTime}')
    print()
    return

#TODO make a big function you can 
# Generate Dataframe
# """
# print()
# print("=== Generating DataFrame ===")
# print()
# dataframe_rows_count = 150_000

# col_data = {
#     'time': np.arange(0, dataframe_rows_count, 1, dtype=int),
#     'tag': np.random.choice(['tag_a', 'tag_b', 'test_c'],
#         size=(dataframe_rows_count,)),
# }
# for n in range(2, 2999):
#     col_data[f'col{n}'] = random.randint(1, 10)

# data_frame = pd.DataFrame(data=col_data).set_index('time')
# print(data_frame)
