import pandas as pd
import os
from nptdms import TdmsFile

# Import ZATAN's Pre Processor Class
import pre_processing

# Import ZATAN's Config Sync Script
import syncConfig

from influxdb_client import Point, InfluxDBClient, WriteOptions  

# from influxdb_client.client.write_api import SYNCHRONOUS

# InfluxDB Token (NEED TO LEARN HOW TO PUT THIS IN THE ENV AND REFERENCE IT)
# Currently I type INFLUXDB_TOKEN=<token> into the console to load it into the
# environment prior to running the script

zatanToken = os.environ.get("INFLUXDB_V2_TOKEN")

pathToFile = "../../tests/081523.tdms"
calib_table_path = '/raw-DAQ-files/sensorCalib.xlsx'

print("initializing processor")
# Creating a Pre_Processor instance
processor = pre_processing.Pre_Processor("../../tests/config.xlsx")
print("initialized processor")
print("\n Printint calib table")
print(processor.calib_table)
print("\n")

_data_frame = processor.get_local_data_as_dataframe(pathToFile)
print("initialized Dataframe")


def multiplier(item, table, sensor, channel):
    return 70 - (item * table[sensor][channel])


print("MADE IT TO DATA PROCESSOR")
tdms_dict = processor.apply_calibration(
   _data_frame, fun=multiplier
)
print("ESCAPED DATA PROCESSOR")
print(tdms_dict)


# # InfluxDB URL - if on dev container use "influx:8086", if on host
# # machine running docker use "localhost:8086". ("127.0.0.1:8086")
# # with InfluxDBClient(url="http://influx:8086", token="zatanToken", org="zatan") as _client:
# with InfluxDBClient(url="http://localhost:8086", token="zatanToken", org="zatan") as _client:
#     with _client.write_api(write_options=WriteOptions(batch_size=500,
#                                                       flush_interval=10_000,
#                                                       jitter_interval=2_000,
#                                                       retry_interval=5_000,
#                                                       max_retries=5,
#                                                       max_retry_delay=30_000,
#                                                       max_close_wait=300_000,
#                                                       exponential_base=2)
#                             ) as _write_client:
#         # Import Pandas DataFrame (needs to be updated further along development)
    


#         pre_processing.Pre_Processor.apply_calibration()





# def main():
#    # nested_dictionaries = syncConfig.process_excel_to_dict(excel_file_path)
#    # print(" \n Printing the Dictionary: \n ")
#     #print(nested_dictionaries)
#     #print(" end dictionary \n")

#     _data_frame = pd.DataFrame()
#     importFrameFromFile(_data_frame, pathToFile)
#     print(" \n Printing the Dataframe: \n ")
#     print(_data_frame)
#     print(" end dataframe \n")
#     _write_client.write("dev", "zatan", record=_data_frame, data_frame_measurement_name='PNB_Reading')
#     #                     data_frame_tag_columns=['location'])
#     print("main")
#     return 0


# main()