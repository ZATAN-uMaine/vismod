from pathlib import Path
from os import environ
import logging

from dotenv import load_dotenv
from flask import Flask, render_template, request, send_file
from werkzeug.middleware.proxy_fix import ProxyFix

from vismod_web.exportInfluxAsCSV import string_process
from vismod_web.exportInfluxAsCSV import query_all_sensors
from vismod_web.exportInfluxAsCSV import query_sensors  # noqa

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


@app.route("/")
def hello():
    return render_template("index.html")


@app.route("/process", methods=["POST", "GET"])
def process():
    data = request.form.get("sensor")
    # process the data using Python code
    return string_process(data)


@app.route("/download_csv", methods=["GET", "POST"])
def download_csv():
    sensor = request.args.get("sensor")
    startDay = request.args.get("startDay")
    startHour = request.args.get("startHour")
    endDay = request.args.get("endDay")
    endHour = request.args.get("endHour")
    start_request = f"{startDay}T{startHour}:00:00.000+04:00"
    end_request = f"{endDay}T{endHour}:00:00.000+04:00"

    if sensor is None:
        return "Missing parameter 'sensor'", 400
    if (
        startDay is None
        or endDay is None
        or startHour is None
        or endHour is None
    ):
        return "Missing time range parameteres", 400

    if sensor == "all":
        logging.info(
            f"""processing download request for all sensors from \
              {start_request} to {end_request}"""
        )
        csv_path = query_all_sensors(start=start_request, stop=end_request)
    else:
        logging.info(
            f"""processing download request for sensor \
              {sensor} from {start_request} to {end_request} """
        )
        csv_path = query_sensors(
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

    logging.info("Finished processing sensor file")
    if csv_path is None:
        logging.info("Telling client that no data was found")
        # HTTP 204 = "No Content"
        return "No data found", 204
    return send_file(
        csv_path,
        mimetype="text/csv",
        as_attachment=True,
        download_name="data.csv",
    )
