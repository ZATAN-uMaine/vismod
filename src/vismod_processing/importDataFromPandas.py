import pandas as pd
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS 
from influxdb_client.extras import pd, np


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

sampleData = [["2023-08-15 04:00:00,", 24.952179, 20914.157433, 20521.860632, 20049.853715, 20914.157433, 20521.860632, 20049.853715, 20914.157433, 20521.860632, 20049.853715, 20914.157433, 20521.860632, 20049.853715, 20914.157433, 20521.860632, 20049.853715, 20914.157433, 20521.860632, 63.541725, 109.980092, 28.137765]]
sampleFrame = pd.DataFrame(sampleData, columns=['_time','17A-TEMP', '17A-Left', '17A-Right', '10A-TEMP', '10A-Left',
       '10A-Right', '2A-TEMP', '2A-Left', '2A-Right', '2B-TEMP', '2B-Left',
       '2B-Right', '10B-TEMP', '10B-Left', '10B-Right', '17B-TEMP', '17B-Left',
       '17B-Right', 'External-Wind-Speed', 'External-Wind-Direction',
       'External-Temperature'],)
    

def uploadDataFrame(df, bucket):
    # Initialize data frame
    dataFrame = df
    bucket = bucket
    #dataFrame["_time"] = pd.to_datetime("_time")
    # Set column as Index
    #dataFrame.set_index('_time', inplace=True)
    #dataFrame.set_index('_time')
    # Transform index to PeriodIndex
    #dataFrame.index = pd.to_datetime(dataFrame.index, unit='s')

    # Initialize Database Client
    print("=== Received dataFrame = ")
    print(dataFrame)
    print()
    print("=== Ingesting DataFrame via batching API ===")
    print()
    startTime = datetime.now()
    with InfluxDBClient(url=link, token=zatanToken, org=organization) as client:

        # Use batching API
        with client.write_api(write_options=SYNCHRONOUS) as write_api:
            write_api.write(bucket=bucket, record=dataFrame,
                            # data_frame_tag_columns=['17A-TEMP', '17A-Left',
                            #      '17A-Right', '10A-TEMP', '10A-Left',
                            #      '10A-Right', '2A-TEMP', '2A-Left', 
                            #      '2A-Right', '2B-TEMP', '2B-Left', 
                            #      '2B-Right', '10B-TEMP', '10B-Left',
                            #      '10B-Right', '17B-TEMP', '17B-Left',
                            #      '17B-Right'],
                            data_frame_tag_columns=['External-Wind-Speed', 'External-Wind-Direction', 'External-Temperature'],
                            data_frame_measurement_name='PNB_Reading')
                           # data_frame_timestamp_column="_time")
                            
            print()
            print("Wait to finishing ingesting DataFrame...")
            print()

    

    print()
    print(f'Import finished in: {datetime.now() - startTime}')
    print()
    return
