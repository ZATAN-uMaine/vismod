from pathlib import Path
from os import environ
from logging import INFO

from dotenv import load_dotenv
from flask import Flask, render_template, request, send_file
from werkzeug.middleware.proxy_fix import ProxyFix

from vismod_processing.exportInfluxAsCSV import string_process


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


@app.route('/process', methods=['POST'])
def process():
    data = request.form.get('sensor')
    # process the data using Python code
    return string_process(data)


@app.route('/download_csv', methods=['GET', 'POST'])
def download_csv():
    file_path = 'test.csv'

    return send_file(
        file_path,
        mimetype='text/csv',
        as_attachment=True,
        download_name="data.csv"
    )