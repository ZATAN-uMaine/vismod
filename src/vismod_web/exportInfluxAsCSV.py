"""
Fetches data from DB for the front end.

here is the full list of sensors (as of 3/3/24):
            [
            "10A-Left", "10A-Right", "10A-TEMP",
            "10B-Left", "10B-Right", "10B-TEMP",
            "17A-Left", "17A-Right", "17A-TEMP",
            "17B-Left", "17B-Right", "17B-TEMP",
            "2A-Left", "2A-Right", "2A-TEMP",
            "2B-Left", "2B-Right", "2B-TEMP",
            "External-Temperature",
            "External-Wind-Direction"
            ]
"""

import os
import csv
import logging
import plotly.graph_objs as go  # type: ignore
from plotly.subplots import make_subplots  # type: ignore
from datetime import datetime
from pathlib import Path
from influxdb_client import InfluxDBClient, Dialect  # type: ignore


# Load database secrets
ourToken = os.environ.get("INFLUXDB_V2_TOKEN")
organization = os.environ.get("INFLUXDB_V2_ORG")
link = os.environ.get("INFLUXDB_V2_URL")
zatan_bucket = os.environ.get("INFLUXDB_V2_BUCKET")

# the plotly_append script allows modifying the theme and functionality
# of the plotly iframe. this snipped loads it from /static.
THEME_TOGGLE_JS = """
  const extraScript = document.createElement('script');
  extraScript.src = "static/plotly_append.js";
  document.head.appendChild(extraScript);
"""

# default values for querying -- these get pruned for specific requests
STRAIN_SENSORS = [  # easier  to add sensors with comprehension (?)
    sensor
    for x in ["2", "10", "17"]
    for sensor in (x + "A-Left", x + "A-Right", x + "B-Left", x + "B-Right")
]

AUXILIARY_SENSORS = [
    "External-Temperature",
    "External-Wind-Direction",
    "External-Wind-Speed",
]
ALL_SENSORS = STRAIN_SENSORS + AUXILIARY_SENSORS

STRAIN_UNITS = {  # every stay gets the same unit
    key: "strain (lbs)" for key in STRAIN_SENSORS
}
AUXILIARY_UNITS = {
    "_time": "UTC",
    "External-Temperature": "degrees (F)",
    "External-Wind-Direction": "angle (degrees)",
    "External-Wind-Speed": "feet/second",
}
ALL_UNITS = {**STRAIN_UNITS, **AUXILIARY_UNITS}

CSV_TMP_PATH = "/tmp"
PLOT_TMP_PATH = "/tmp"


def generate_file_name(start, stop, file_type):
    """
    This method generates the file name for the output file
    It takes a start time and a stop time as input.
    The format for these times is RFC3339.
    """
    # Remove time-related characters from start and stop dates
    start_dt = datetime.strptime(start, '%Y-%m-%dT%H:%M:%S.%fZ')
    stop_dt = datetime.strptime(stop, '%Y-%m-%dT%H:%M:%S.%fZ')

    fileStartDate = start_dt.strftime('%Y-%m-%d')
    fileStopDate = stop_dt.strftime('%Y-%m-%d')

    extension = {"Reading": "csv", "Plot": "html"}.get(file_type)

    # stamping with milliseconds
    now = datetime.now()
    time_since_midnight = now - now.replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    ms = round(time_since_midnight.total_seconds() * 1000)
    file_name = (
        f"PNB_{file_type}_{fileStartDate}_to_{fileStopDate}_{ms}.{extension}"
    )

    return file_name


def format_sensor_list(sensors):
    """
    This method takes the list of sensors as input
    and outputs them into a formatted query string
    to be injected into the query.
    """
    # require that the passed sensors match pre-determined sensors
    received_sensors = [sensor for sensor in sensors if sensor in ALL_SENSORS]
    logging.debug(f"Valid sensors received: {received_sensors}")

    for index, item in enumerate(received_sensors):
        if index == 0:
            received_sensors[index] = 'r["node"] == "' + item + '"'
        else:
            received_sensors[index] = ' or r["node"] == "' + item + '"'
    partially_formatted_sensors = "".join(received_sensors)
    logging.debug(
        f"partial format applied: {repr(partially_formatted_sensors)}"
    )
    formatted_sensors = partially_formatted_sensors.replace('"', '"')
    return formatted_sensors


def get_sensor_data_range():
    """
     Returns a tuple of timestamps and float,
    (first reading, last reading, reading count).
     If there's an error, return None.
    """
    with InfluxDBClient(url=link, token=ourToken, org=organization) as client:
        fdq_results = client.query_api().query(
            f"""
              from(bucket: "{zatan_bucket}")
              |> range(start: 0)
              |> filter(fn: (r) => r["_measurement"] == "NodeStrain")
              |> group()
              |> keep(columns: ["_time", "_value"])
              |> first()
            """
        )
        flat_fdq_res = fdq_results.to_values(columns=["_time"])
        if flat_fdq_res is None or len(flat_fdq_res) != 1:
            logging.error("Failed to find time of first reading")
            return None
        first_reading_time = flat_fdq_res[0][0]
        ldq_results = client.query_api().query(
            f"""
              from(bucket: "{zatan_bucket}")
              |> range(start: 0)
              |> filter(fn: (r) => r["_measurement"] == "NodeStrain")
              |> group()
              |> keep(columns: ["_time", "_value"])
              |> last()
            """
        )
        flat_ldq_res = ldq_results.to_values(columns=["_time"])
        if flat_ldq_res is None or len(flat_ldq_res) != 1:
            logging.error("Failed to find time of last reading")
            return None
        last_reading_time = flat_ldq_res[0][0]
        len_results = client.query_api().query(
            f"""
              from(bucket: "{zatan_bucket}")
                |> range(start: 0)
                |> filter(fn: (r) => r["_measurement"] == "NodeStrain")
                |> filter(fn: (r) => r["_field"] == "_value")
                |> filter(fn: (r) => r["node"] == "2A-Left")
                |> group()
                |> count()
            """
        )
        flat_len_res = len_results.to_values(columns=["_value"])
        if flat_len_res is not None and len(flat_len_res) == 1:
            reading_count = flat_len_res[0][0]
        else:
            reading_count = 0
        logging.debug(
            f"fetched summary statistics {first_reading_time} {last_reading_time} {reading_count}"  # noqa
        )
        return (first_reading_time, last_reading_time, reading_count)


def query_sensors_for_CSV(start, stop, sensors):
    """
    query_sensors_for_CSV is our custom and most up to date
    querying method. It takes a start time, stop time,
    and a list of desired sensors as input.

                    "External-Wind-Speed"]
        # to query your sensor follow the following format (EST):
        # exportInfluxAsCSV.querySensors(
        # 'YYYY-MM-DDT00:00:00.000+04:00',
        # 'YYYY-MM-DDT00:00:00.000+04:00',
        # [<sensorlist>])
        # INCLUDE "_measurement" as an item in sensor list!!!
    """
    parent = Path(CSV_TMP_PATH)
    csv_path = generate_file_name(start, stop, "Reading")
    write_to = parent / csv_path
    formatted_sensors = format_sensor_list(sensors)
    logging.info(f"Querying sensors: {sensors} from {start} to {stop}")

    export_start_time = datetime.now()
    with InfluxDBClient(url=link, token=ourToken, org=organization) as client:
        csv_iterator = client.query_api().query_csv(
            """
                from(bucket: "{bucket_name}")
                |> range(start: {start_time},
                  stop: {stop_time})
                |> filter(fn: (r) => r["_measurement"] == "NodeStrain")
                |> filter(fn: (r) => r["_field"] == "_value")
                |> filter(fn: (r) => {sensor_list})
                |> pivot(rowKey:["_time"],
                         columnKey: ["node"],
                         valueColumn: "_value")
                |> group()
                |> drop(columns:
                    ["result","_start","_stop","_measurement","_field"])
            """.format(
                bucket_name=str(zatan_bucket),
                start_time=start,
                stop_time=stop,
                sensor_list=formatted_sensors,
            ),
            dialect=Dialect(
                header=True,
                annotations=[],
                date_time_format="RFC3339",
                delimiter=",",
            ),
        )
        output = csv_iterator.to_values()
        logging.info(f"Found {len(output)} rows to export")
        if len(output) == 0:
            return None

        with open(write_to, mode="w", newline="") as file:
            writer = csv.writer(file)

            header_row = output[0][3:]
            writer.writerow(header_row)

            units = [ALL_UNITS[column] for column in header_row]
            writer.writerow(units)

            for row in output[1:]:  # the rest of the output
                writer.writerow(row[3:])

    logging.info(f"Export finished in: {datetime.now() - export_start_time}")
    return write_to


def query_all_sensors_for_CSV(start, stop):
    """
    This method is used to query all sensors
    It takes a start time and a stop time as input.
    The format for these times is RFC3339.
    """
    parent = Path(CSV_TMP_PATH)
    csv_path = generate_file_name(start, stop, "Reading")
    write_to = parent / csv_path
    logging.info(f"exporting data from all sensors to {write_to}")
    formatted_sensors = format_sensor_list(ALL_SENSORS)

    export_start_time = datetime.now()
    with InfluxDBClient(url=link, token=ourToken, org=organization) as client:
        # Query All Sensors
        csv_iterator = client.query_api().query_csv(
            f"""
                from(bucket: "{zatan_bucket}")
                |> range(start: {start},
                  stop: {stop})
                |> filter(fn: (r) => r["_measurement"] == "NodeStrain")
                |> filter(fn: (r) => r["_field"] == "_value")
                |> filter(fn: (r) => {formatted_sensors})
                |>pivot(rowKey:["_time"],
                         columnKey: ["node"],
                         valueColumn: "_value")
                |> group()
                |> drop(columns:
                        ["result","_start","_stop","_measurement","_field"])
            """,
            dialect=Dialect(
                header=True,
                annotations=[],
                date_time_format="RFC3339",
                delimiter=",",
            ),
        )

        output = csv_iterator.to_values()
        logging.info(f"Found {len(output)} rows to export")

        with open(write_to, mode="w", newline="") as file:
            writer = csv.writer(file)

            header_row = output[0][3:]
            writer.writerow(header_row)

            units = [ALL_UNITS[column] for column in header_row]
            writer.writerow(units)

            for row in output[1:]:  # the rest of the output
                writer.writerow(row[3:])
    logging.info(f"Export finished in: {datetime.now() - export_start_time}")
    return write_to


def query_all_sensors_for_plot(start, stop, sensors, aggregate=120):
    """
    This function is very similar to
    query_sensors_for_CSV, but writes an HTML
    as a string, containing a plotly plot.
    This string gets passed to the front end
    and written into an iframe.
    """

    formatted_sensors = format_sensor_list(ALL_SENSORS)

    logging.info(
        f"Querying all sensors from {start} to {stop}, every {aggregate} seconds"  # noqa
    )

    with InfluxDBClient(url=link, token=ourToken, org=organization) as client:
        plot_query = f"""
                from(bucket: "{zatan_bucket}")
                |> range(start: {start},
                  stop: {stop})
                |> filter(fn: (r) => r["_measurement"] == "NodeStrain")
                |> filter(fn: (r) => r["_field"] == "_value")
                |> filter(fn: (r) => {formatted_sensors})
                |> aggregateWindow(every: {aggregate}s, fn: mean)
                |>pivot(rowKey:["_time"],
                         columnKey: ["node"],
                         valueColumn: "_value")
                |> group()
                |> fill(value: 0.0)
                |> drop(columns:
                    ["result","_start","_stop","_measurement","_field"])
            """

        result = client.query_api().query(plot_query, org=organization)
        filtered_sensors = [
            sensor for sensor in sensors if sensor in ALL_SENSORS
        ]

        results_dict = {  # _time join to the sensors, each key gets empty list
            key: [] for key in ["_time"] + ALL_SENSORS
        }

        # this should be the _time column + sensors
        column_keys = list(results_dict.keys())

        for table in result:
            for record in table.records:  # each row
                for k in column_keys:
                    results_dict[k].append(record[k])

        plot_html = create_plot(results_dict, filtered_sensors)
        return plot_html


# WIP: need to better parameterize strain and weather nodes to simplify logic


def create_plot(results_dict, filtered_sensors):
    """
    Auxiliary function for handling the details
    of plot creation with plotly.
    Be careful -- this function assumes that the
    data results_dict is formatted in a particular
    way, based on the Flask route.
    """
    print(
        "filtered sensors passed to plot creation: {filtered_sensors}".format(
            filtered_sensors=filtered_sensors
        )
    )

    if not results_dict["_time"]:
        return "<div>No data available for the selected date range.</div>"

    fig = make_subplots(
        specs=[[{"secondary_y": True}]],
        rows=1,
        cols=1,
        shared_xaxes=True,
        shared_yaxes=False,
    )
    # get first and last timestamps from the _time column
    start_stamp = results_dict["_time"][0].strftime("%Y %b %d %H:%M")
    end_stamp = results_dict["_time"][-1].strftime("%Y %b %d %H:%M")

    plot_title = "Stay {name} strain from {st} to {et}".format(
        name=filtered_sensors[0].split("-")[0], st=start_stamp, et=end_stamp
    )
    layout = go.Layout(
        title=plot_title,
        template="plotly",
        xaxis=dict(
            title="Time Stamp (UTC)",
            gridcolor="#C0C0C0",
            zerolinecolor="#B0B0B0",
        ),
        yaxis=dict(title="Strain (lbs)", gridcolor="#B0B0B0"),
        yaxis2=dict(
            title="Temperature (F)",
            overlaying="y",
            side="right",
            gridcolor="#B0B0B0",
            zerolinecolor="#B0B0B0",
        ),
    )
    weather_layout = go.Layout(
        title=plot_title,
        template="plotly",
        xaxis=dict(title="Time Stamp (UTC)"),
        yaxis=dict(title="Temperature (F)"),
        yaxis2=dict(title="Feet per Second", overlaying="y", side="right"),
        yaxis3=dict(title="Degrees", overlaying="y", side="right"),
    )

    if filtered_sensors[0] not in AUXILIARY_SENSORS:
        fig.update_layout(layout)
        strain_flag = True
    else:
        fig.update_layout(weather_layout)
        strain_flag = False

    trace_color_list = [
        "red",
        "blue",
        "green",
        "yellow",
        "purple",
        "orange",
        "olive",
        "gray",
        "aqua",
        "fuchsia",
        "chartreuse",
        "indigo",
        "gold",
        "mediumaquamarine",
    ]

    for i, sensor in enumerate(filtered_sensors):
        if (
            (sensor in AUXILIARY_SENSORS) and (strain_flag)
        ) or sensor == "External-Wind-Speed":
            continue

        fig.add_trace(
            go.Scatter(
                mode="lines+markers",
                x=results_dict["_time"],
                y=results_dict[sensor],
                name=sensor,
                marker=dict(
                    color=trace_color_list[i % 14], symbol="diamond", size=5
                ),
                line=dict(dash="solid"),
            ),
            secondary_y=False,
        )

    for i, sensor in enumerate(STRAIN_SENSORS):
        if sensor in filtered_sensors:
            continue
        else:
            if filtered_sensors[0] in AUXILIARY_SENSORS:
                continue
            else:
                index = -(i % 14)
                print("color index: {index}".format(index=index))

                print(
                    "color value: {iterator}".format(
                        iterator=trace_color_list[index]
                    )
                )

                fig.add_trace(
                    go.Scatter(
                        mode="lines+markers",
                        x=results_dict["_time"],
                        y=results_dict[STRAIN_SENSORS[i]],
                        name=sensor,
                        marker=dict(
                            color=trace_color_list[index],
                            symbol="diamond",
                            size=5,
                        ),
                        line=dict(dash="solid"),
                        visible="legendonly",
                    ),
                    secondary_y=False,
                )

    # draw the external temperature
    # assumes that the External-Temp sensor is in the last
    # index of the filered_sensors list
    if filtered_sensors[0] not in AUXILIARY_SENSORS:
        fig.add_trace(
            go.Scatter(
                mode="lines+markers",
                x=results_dict["_time"],
                y=results_dict[filtered_sensors[-1]],
                name="External Temperature (F)",
                marker=dict(color="lightblue", symbol="diamond", size=3),
                line=dict(dash="dash"),
                visible="legendonly",
            ),
            secondary_y=True,
        )
    else:
        print("adding second weather axis")
        fig.add_trace(
            go.Scatter(
                mode="lines+markers",
                x=results_dict["_time"],
                y=results_dict[filtered_sensors[0]],
                name="Wind Speed (F/S)",
                marker=dict(color="darksalmon", symbol="diamond", size=3),
                line=dict(dash="dash"),
                visible="legendonly",
            ),
            secondary_y=True,
        )
    # returns a huge string containing all the HTML needed
    # to display the plot
    return fig.to_html(
        include_mathjax=False,
        include_plotlyjs="static/plotly-2.30.0.min.js",
        div_id="our-plot",
        post_script=THEME_TOGGLE_JS,
    )