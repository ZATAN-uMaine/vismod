import os
import json
from datetime import datetime
from io import StringIO

from dotenv import load_dotenv
import requests
import pandas as pd


def config_to_json(csv_content: str, save_file=False):
    """
    Turns CSV config file (as string) into the standard
    JSON representation. Can optionally save a copy as data.json.
    """

    # Set the header row to the row containing the column names
    config_df = pd.read_csv(StringIO(csv_content), header=2)

    # Contact information is stored in the first column below row 4
    contactinfo = config_df.iloc[1:, 0].dropna().tolist()

    # Initialize dictionaries
    nested_dictionaries = {
        "Load Cells": {},
        "Wind Sensor": {},
        "Contact Info": [],
        "Last Modified": "",
    }

    # Add contact info and last modified timestamp
    nested_dictionaries["Contact Info"] = contactinfo
    nested_dictionaries["Last Modified"] = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    for index, row in config_df.iterrows():
        if pd.notna(row["Node"]):
            if index == 0:  # Skip first row, which holds info about the header
                continue
            elif index == config_df.index[-1]:  # Check if this is the last row
                # Process differently for Wind Sensor
                nested_dictionaries["Wind Sensor"]["Sensor ID"] = row["Node"]
            else:
                node = str(row["Node"])
                if node not in nested_dictionaries["Load Cells"]:
                    nested_dictionaries["Load Cells"][node] = {}
                    # Initialize if not exist

                wdaq_key = str(row.get("WDAQ_L", None))
                prefix = wdaq_key.split("_")[0]  # Extract prefix

                prefixed_keys = {
                    f"{prefix}-Cal_Factor": row.get("Cal Factor_L", None),
                    f"{prefix}-Cable ID": row.get("Cable ID", None),
                    f"{prefix}-TEMP": row.get("Cal Factor_T", None),
                }

                for key, value in prefixed_keys.items():
                    nested_dictionaries["Load Cells"][node][key] = value

    # Convert dictionaries to JSON
    json_data = json.dumps(nested_dictionaries, indent=4)

    # Write JSON data to file
    if save_file:
        print("Saving config to data.json")
        with open("data.json", "w") as file:
            file.write(json_data)

    return nested_dictionaries


def download_config(save_file=False):
    CONFIG_ID = os.getenv("CONFIG_ID")

    # Construct the URL for exporting the sheet as a CSV
    url = (
        f"https://docs.google.com/spreadsheets/d/{CONFIG_ID}/"
        "export?format=csv"
    )

    # Make a GET request to download the file
    response = requests.get(url)
    # If the request was unsuccessful in any way, print the error and return
    if response.status_code != 200:
        print(f"Request failed ({response.status_code}), : {response.text}")
        return None

    print("File downloaded successfully")
    str_content = response.content.decode("utf-8")
    print("CSV extracted from file")
    return config_to_json(str_content, save_file=save_file)


# Allow this file to be run standalone
if __name__ == "__main__":
    load_dotenv()
    nested_dictionaries = download_config(save_file=True)
