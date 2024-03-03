import os
import csv
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
from influxdb_client import InfluxDBClient, Dialect

# Load environment
load_dotenv(dotenv_path=Path(".env"))

# Load database secrets
zatanToken = os.environ.get("INFLUXDB_V2_TOKEN")
organization = os.environ.get("INFLUXDB_V2_ORG")
link = os.environ.get("INFLUXDB_V2_URL")


def queryAllSensors(start, stop):
    
    exportStartTime = datetime.now()
    with InfluxDBClient(url=link, token=zatanToken, org=organization) as client:
        # Query: using CSV iterator

        #csv_iterator = client.query_api().query_csv(f'from(bucket:"dev") |> range(start: {start} stop: {stop})',
        
        #Query Everything 1,000,000 minutes in the past from the dev bucket
        csv_iterator = client.query_api().query_csv('''from(bucket:"dev") |> range(start: -1000000m)''', dialect=Dialect(header=False, annotations=[], date_time_format='RFC3339', delimiter=","))

        
        output = csv_iterator.to_values()
        #print(output)
        print()
        with open('test.csv', mode='w', newline='') as file:
            print("writing to file")
            writer = csv.writer(file)
            writer.writerows(output)          
    print()
    print(f"Export finished in: {datetime.now() - exportStartTime}")
    print()
    return

def querySensors10AB(start, stop):
    
    exportStartTime = datetime.now()
    with InfluxDBClient(url=link, token=zatanToken, org=organization) as client:
        # Query: using CSV iterator

        #csv_iterator = client.query_api().query_csv(f'from(bucket:"dev") |> range(start: {start} stop: {stop})',
        
        #Query Everything 1,000,000 minutes in the past from the dev bucket
        csv_iterator = client.query_api().query_csv('''from(bucket:"dev") |> range(start: -1000000m)''', dialect=Dialect(header=False, annotations=[], date_time_format='RFC3339', delimiter=","))

        output = csv_iterator.to_values()
        # print(output)
        print()

        with open('test.csv', mode='w', newline='') as file:
            print("writing to file")
            writer = csv.writer(file)
            writer.writerows(output)    

    print()
    print(f"Export finished in: {datetime.now() - exportStartTime}")
    print()
    return
