from pathlib import Path
from os import environ
from logging import INFO

from dotenv import load_dotenv
from flask import Flask, render_template, request, send_file
from werkzeug.middleware.proxy_fix import ProxyFix

from vismod_processing.exportInfluxAsCSV import string_process
from vismod_processing.exportInfluxAsCSV import query_all_sensors

load_dotenv(dotenv_path=Path(".env"))

app = Flask(__name__)
# use the builtin flask logger to make formatted logging entries
app.logger.setLevel(INFO)

# need special settings to run Flask behind nginx proxy
if (
    environ.get("FLASK_ENV") is not None
    and environ.get("FLASK_ENV") == "production"
):
    app.logger.info("Flask running in production mode. Proxy enabled.")
    app.wsgi_app = ProxyFix(
        app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
    )
else:
    app.logger.info("Flask running in development mode.")


@app.route("/")
def hello():
    return render_template("index.html")


@app.route('/process', methods=['POST', 'GET'])
def process():
    data = request.form.get('sensor')
    # process the data using Python code
    return string_process(data)


@app.route('/download_csv', methods=['GET', 'POST'])
def download_csv():
    # sensor = request.args.get('sensor')
    startDay = request.args.get('startDay')
    startHour = request.args.get('startHour')
    endDay = request.args.get('endDay')
    endHour = request.args.get('endHour')

    start_request = f"{startDay}T{startHour}:00:00.000+4:00"
    end_request = f"{endDay}T{endHour}:00:00.000+4:00"

    file = str(query_all_sensors(start=start_request, stop=end_request))
    return file


@app.route('/test_download', methods=['GET'])
def test_download():
    file_path = 'user_csvs/test.csv'

    return send_file(
        file_path,
        mimetype='text/csv',
        as_attachment=True,
        download_name="data.csv"
    )
