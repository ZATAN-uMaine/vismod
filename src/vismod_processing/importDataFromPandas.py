import pandas as pd
import os
import csv
from datetime import datetime, timedelta
import reactivex as rx
from reactivex import operators as ops
from nptdms import TdmsFile

#Import ZATAN's Pre Processor Class
import pre_processing

#Import ZATAN's Config Sync Script
import syncConfig

from influxdb_client import Point, InfluxDBClient, WriteOptions  

# from influxdb_client.client.write_api import SYNCHRONOUS

# InfluxDB Token (NEED TO LEARN HOW TO PUT THIS IN THE ENV AND REFERENCE IT)
# Currently I type INFLUXDB_TOKEN=<token> into the console to load it into the environment prior to running the script

#zatanToken =  os.environ.get("INFLUXDB_TOKEN")

zatanToken = "ulIEuO_JraLqvnMXRf8qraQRoCQXJKiPD7VCvVUp02JOPGIWU9xNnQU_Bd0-dhM40Je8UtnetLQgUyePT39J5w=="
pathToFile = "..//..//tests//081523.tdms"
processor = pre_processing.Pre_Processor(pathToFile)


# InfluxDB URL - if on dev container use "influx:8086", if on host
# machine running docker use "localhost:8086". ("127.0.0.1:8086")

# with InfluxDBClient(url="http://influx:8086", token="zatanToken", org="zatan") as _client:
with InfluxDBClient(url="http://localhost:8086", token="zatanToken", org="zatan") as _client:

    with _client.write_api(write_options=WriteOptions(batch_size=500,
                                                      flush_interval=10_000,
                                                      jitter_interval=2_000,
                                                      retry_interval=5_000,
                                                      max_retries=5,
                                                      max_retry_delay=30_000,
                                                      max_close_wait=300_000,
                                                      exponential_base=2)
                            ) as _write_client:


       # Import Pandas DataFrame (needs to be updated further along development)
        def importFrameFromFile(processor, pathToFile):
            path = pathToFile
            self = processor
            tdms_frame = pre_processing.Pre_Processor.get_local_data_as_dataframe(
            self, path        
        )
            with TdmsFile.open(pathToFile) as tdms_file:
                return tdms_file.as_dataframe()        

       # Write Pandas DataFrame

        # _now = datetime.utcnow()
        # _data_frame = pd.DataFrame(data=[["coyote_creek", 1.0], ["coyote_creek", 2.0]],
        #                            index=[_now, _now + timedelta(hours=1)],
        #                            columns=["location", "water_level"])

        # 
        #Import calibration table dictionary
        excel_file_path = 'config.xlsx'



        # Write Dictionary-style object

        # _write_client.write("dev", "zatan",
        #     {"measurement": "calibrationTable",
        #      "tags": {"node1": "43641", "node2": "43644","node3": "43642", "node4": "45616", "node5": "43643", "node6": "45617" },
        #      "fields": {"Cable ID": "17A-Left", }, })
        # _write_client.write("my-bucket", "my-org", [{"measurement": "h2o_feet", "tags": {"location": "coyote_creek"},
        #                                              "fields": {"water_level": 2.0}, "time": 2},
        #                                             {"measurement": "h2o_feet", "tags": {"location": "coyote_creek"},
        #                                              "fields": {"water_level": 3.0}, "time": 3}])


def main():

    nested_dictionaries = syncConfig.process_excel_to_dict(excel_file_path)
    print(" \n Printing the Dictionary: \n ")
    print(nested_dictionaries)
    print(" end dictionary \n")

    _data_frame = pd.DataFrame()
    importFrameFromFile(_data_frame, pathToFile)
    print(" \n Printing the Dataframe: \n ")
    print(_data_frame)
    print(" end dataframe \n")


    _write_client.write("dev", "zatan", record=_data_frame, data_frame_measurement_name='PNB_Reading')
        #                     data_frame_tag_columns=['location'])
    print("main")
    return 0

main()