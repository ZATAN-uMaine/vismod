from collections import OrderedDict
from csv import DictReader
from itertools import islice
import os
import csv
import reactivex as rx
from reactivex import operators as ops

from influxdb_client import Point, InfluxDBClient, WriteOptions  # , WritePrecision


# from influxdb_client.client.write_api import SYNCHRONOUS

# InfluxDB Token (NEED TO LEARN HOW TO PUT THIS IN THE ENV AND REFERENCE IT)
# Currently I type INFLUXDB_TOKEN=<token> into the console to load it into the environment prior to running the script
zatanToken = "ulIEuO_JraLqvnMXRf8qraQRoCQXJKiPD7VCvVUp02JOPGIWU9xNnQU_Bd0-dhM40Je8UtnetLQgUyePT39J5w==" # os.environ.get("INFLUXDB_TOKEN")

input_file = 'test.csv'
output_file = 'influxReady.csv'

def remove_second_row(input_file, output_file):
    with open(input_file, 'r', newline='') as infile:
        reader = csv.reader(infile)
        rows = []
        for index, row in enumerate(reader):
            if index != 1:  # Skip the second row
                rows.append(row)
                
    with open(output_file, 'w', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerows(rows)


remove_second_row(input_file, output_file)


def parse_row(row: OrderedDict):
    """
    :param row: the row of CSV file
    :return: Parsed csv row to [Point]
    """

    """
    For better performance is sometimes useful directly create a LineProtocol to avoid unnecessary escaping overhead:
    """
    # from datetime import timezone
    # import ciso8601
    # from influxdb_client.client.write.point import EPOCH
    #
    # time = (ciso8601.parse_datetime(row["Date"]).replace(tzinfo=timezone.utc) - EPOCH).total_seconds() * 1e9
    # return f"financial-analysis,type=vix-daily" \
    #        f" close={float(row['VIX Close'])},high={float(row['VIX High'])},low={float(row['VIX Low'])},open={float(row['VIX Open'])} " \
    #        f" {int(time)}"

    return Point("PNB-Reading") \
        .tag("windDirection", float(row['WindDir'])) \
        .tag("windSpeed", float(row['WindSpd'])) \
        .tag("ambientTemperature", float(row['TA'])) \
        .tag("T14441", float(row['T14441']))\
        .tag("Sensor", "17ALeft")\
        .field("17ALeft-LoadCell", float(row['17AL-LC']))\
        .field("17ALeft-Temperature", float(row['17AL-T']))\
        .tag("Sensor", "17ARight")\
        .field("17ARight-LoadCell", float(row['17AR-LC']))\
        .field("T43641", float(row['T43641']))\
        .tag("Sensor", "17BLeft")\
        .field("17BLeft-LoadCell", float(row['17BL-LC']))\
        .field("17BLeft-Temperature", float(row['17BL-T']))\
        .tag("Sensor", "17BRight")\
        .field("17BRight-LoadCell", float(row['17BR-LC']))\
        .field("T45617", float(row['T45617']))\
        .tag("Sensor", "10ALeft")\
        .field("10ALeft-LoadCell", float(row['10AL-LC']))\
        .field("10ALeft-Temperature", float(row['10AL-T']))\
        .tag("Sensor", "10ARight")\
        .field("10ARight-LoadCell", float(row['10AR-LC']))\
        .field("T43644", float(row['T43644']))\
        .tag("Sensor", "10BLeft")\
        .field("10BLeft-LoadCell", float(row['10BL-LC']))\
        .field("10BLeft-Temperature", float(row['10BL-T']))\
        .tag("Sensor", "10BRight")\
        .field("10BRight-LoadCell", float(row['10BR-LC']))\
        .field("T43643", float(row['T43643']))\
        .tag("Sensor", "2ALeft")\
        .field("2ALeft-LoadCell", float(row['2AL-LC']))\
        .field("2ALeft-Temperature", float(row['2AL-T']))\
        .tag("Sensor", "2ARight")\
        .field("2ARight-LoadCell", float(row['2AR-LC']))\
        .field("T43642", float(row['T43642']))\
        .tag("Sensor", "2BLeft")\
        .field("2BLeft-LoadCell", float(row['2BL-LC']))\
        .field("2BLeft-Temperature", float(row['2BL-T']))\
        .tag("Sensor", "2BRight")\
        .field("2BRight-LoadCell", float(row['2BR-LC']))\
        .field("T45616", float(row['T45616']))\
        .time(row['Date Time'])
    #    .field("close", float(row['VIX Close'])) \



"""
Converts test.csv into sequence of data point
"""
data = rx \
    .from_iterable(DictReader(open('influxReady.csv', 'r'))) \
    .pipe(ops.map(lambda row: parse_row(row)))

with InfluxDBClient(url="http://influx:8086", token=zatanToken, org="zatan", debug=True) as client:

    """
    Create client that writes data in batches with 50_000 items.
    """
    with client.write_api(write_options=WriteOptions(batch_size=50_000, flush_interval=10_000)) as write_api:

        """
        Write data into InfluxDB
        """
        write_api.write(bucket="dev", record=data)

    """
    Querying max value of CBOE Volatility Index
    """
    query = 'from(bucket:"dev")' \
            ' |> range(start: 0, stop: now())' \
            ' |> filter(fn: (r) => r._measurement == "PNB-Reading")' \
            ' |> max()'
    result = client.query_api().query(query=query)

    """
    Processing results
    """
    print()
    print("=== results (not working) ===")
    print()
    # for table in result:
    #    for record in table.records:
    #    print()
    

