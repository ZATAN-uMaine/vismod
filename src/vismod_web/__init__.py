from pathlib import Path
from os import environ
import logging

from dotenv import load_dotenv
from flask import Flask, render_template, request, send_file, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix

from vismod_web.exportInfluxAsCSV import (
    query_all_sensors_for_CSV,
    query_sensors_for_CSV,
    get_sensor_data_range,
    query_all_sensors_for_plot,
)

load_dotenv(dotenv_path=Path(".env"))

app = Flask(__name__)
# get HTTP access log from app logger
app.logger.setLevel(logging.INFO)
# setup logging to stdout
logging.basicConfig(level=logging.INFO)

# need special settings to run Flask behind nginx proxy
if (
    environ.get("FLASK_ENV") is not None
    and environ.get("FLASK_ENV") == "production"
):
    logging.info("Flask running in production mode. Proxy enabled.")
    app.wsgi_app = ProxyFix(
        app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
    )
else:
    logging.info("Flask running in development mode.")
    # will reload HTML / CSS / JS after change without restarting the server
    app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.route("/")
def index():
    (start, stop, count) = get_sensor_data_range()
    return render_template(
        "index.html", data={"start": start, "stop": stop, "count": count}
    )


@app.route("/process", methods=["POST", "GET"])
def process():
    data = request.form.get("sensor")
    # process the data using Python code
    return data * 2


@app.route("/download_csv", methods=["GET", "POST"])
def download_csv():
    sensor = request.values.get("sensor")
    start_request = request.values.get("start")
    end_request = request.values.get("end")
    print((start_request, end_request))

    if sensor is None:
        return "Missing parameter 'sensor'", 400
    if start_request is None or end_request is None:
        return "Missing time range parameteres", 400

    if sensor == "all":
        logging.info(
            f"""processing download request for all sensors from \
              {start_request} to {end_request}"""
        )
        file = str(
            query_all_sensors_for_CSV(start=start_request, stop=end_request)
        )
    else:
        logging.info(
            f"""processing download request for sensor \
              {sensor} from {start_request} to {end_request} """
        )
        file = str(
            query_sensors_for_CSV(
                start=start_request,
                stop=end_request,
                sensors=[
                    sensor,
                    sensor + "-Left",
                    sensor + "-Right",
                    "External-Temperature",
                    "External-Wind-Direction",
                    "External-Wind-Speed",
                ],
            )
        )
        if file is None:
            return "No data found", 204

    logging.info("Finished processing sensor file")
    return send_file(
        file, mimetype="text/csv", as_attachment=True, download_name="data.csv"
    )


@app.route("/display_plot", methods=["GET", "POST"])
def display_plot():
    sensor = request.values.get("sensor")
    start_request = request.values.get("start")
    end_request = request.values.get("end")

    if sensor is None:
        return "Missing parameter 'sensor'", 400
    if start_request is None or end_request is None:
        return "Missing time range parameteres", 400

    logging.info(
        f"""processing download request for sensor \
            {sensor} from {start_request} to {end_request} """
    )
    plot_html = str(
        query_all_sensors_for_plot(
            start=start_request,
            stop=end_request,
            sensors=[
                sensor,
                sensor + "-Left",
                sensor + "-Right",
                "External_Temperature",
            ],
        )
    )

    return plot_html


@app.route("/available_data", methods=["POST"])
def available_data():
    (start, end, count) = get_sensor_data_range()
    return jsonify({"start": start, "end": end, "count": count})
