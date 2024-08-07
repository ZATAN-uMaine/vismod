import os
import json
import logging
from io import StringIO
from dotenv import load_dotenv
import requests
import pandas as pd


def config_to_json(csv_content: str, save_file=False):
    """
    Turns CSV config file (as string) into the standard
    JSON representation. Can optionally save a copy as data.json.

    Returns None and logs warning if invalid.
    """
    # Set the header row to the row containing the column names
    try:
        config_df = pd.read_csv(StringIO(csv_content), header=2)
    except UnicodeError:
        logging.warn("Could not read downloaded file as CSV")
        return None

    # Contact information is stored in the first column below row 4
    contactinfo = config_df.iloc[1:, 0].dropna().tolist()

    # Initialize return value
    nested_dictionaries = {
        "Load Cells": {},
        "Wind Sensor": {},
        "Contact Info": [],
    }

    # Add contact info and last modified timestamp
    nested_dictionaries["Contact Info"] = contactinfo

    # Iterate through the rows of the CSV and populate the nested dictionary
    for index, row in config_df.iterrows():
        if pd.notna(row["Node"]):
            # Skip first row, which holds info about the header
            if index == 0:
                continue

            # Process differently for Wind Sensor
            elif index == config_df.index[-1]:
                nested_dictionaries["Wind Sensor"]["Sensor ID"] = row["Node"]

            # Process differently for Load Cells
            else:
                node = str(row["Node"])

                # If the node is not in the dictionary, add it
                if node not in nested_dictionaries["Load Cells"]:
                    nested_dictionaries["Load Cells"][node] = {}

                # Extract WDAQ key and prefix
                wdaq_key = str(row.get("WDAQ_L", None))
                prefix = wdaq_key.split("_")[0]

                # Add the WDAQ key to the dictionary
                prefixed_keys = {
                    f"{prefix}-Cal_Factor": float(
                        row.get("Cal Factor_L", 0.0)
                    ),  # noqa
                    f"{prefix}-Cable ID": row.get("Cable ID", None),
                    f"{prefix}-TEMP": float(row.get("Cal Factor_T", 0.0)),
                }

                # Add the data to the dictionary
                for key, value in prefixed_keys.items():
                    nested_dictionaries["Load Cells"][node][key] = value

    # Convert dictionaries to JSON
    json_data = json.dumps(nested_dictionaries, indent=4)

    # Write JSON data to file
    if save_file:
        logging.info("Saving config to data.json")
        with open("data.json", "w") as file:
            file.write(json_data)

    return nested_dictionaries


def download_config(save_file=False):
    """
    Downloads the config file from Google Sheets and converts it to JSON.
    Optionally saves the JSON to data.json.
    Return None if something breaks.
    """
    CONFIG_ID = os.getenv("CONFIG_ID")
    if not CONFIG_ID or len(CONFIG_ID) < 5:
        logging.error("$CONFIG_ID not provided by environment")
        return None

    # Construct the URL for exporting the sheet as a CSV
    url = (
        f"https://docs.google.com/spreadsheets/d/{CONFIG_ID}/"
        "export?format=csv"
    )

    logging.info(f"Attempting to fetch config file from {url}")
    # Request the file from the URL
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.warn(f"Request failed: {e}")
        return None

    logging.info("Config file downloaded successfully")
    try:
        str_content = response.content.decode("utf-8")
        return config_to_json(str_content, save_file=save_file)
    except UnicodeError:
        logging.warn("Could not decode downloaded config file as utf-8")
        return None


# Allow this file to be run standalone
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    load_dotenv()
    nested_dictionaries = download_config(save_file=True)
