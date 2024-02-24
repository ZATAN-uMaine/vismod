import os
from dotenv import load_dotenv
import requests
import pandas as pd
import json
from datetime import datetime


def read_config():
    # Set the header row to the row containing the column names
    config_df = pd.read_csv("config.csv", header=2)

    # Contact information is stored in the first column below row 4
    contactinfo = config_df.iloc[1:, 0].dropna().tolist()

    # Initialize dictionaries
    nested_dictionaries = {
        "Load Cells": {},
        "Wind Sensor": {},
        "Contact Info": [],
        "Last Modified": ""
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
                prefix = wdaq_key.split('_')[0]  # Extract prefix

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
    with open("data.json", "w") as file:
        file.write(json_data)


def download_config():
    # Load environment variables
    load_dotenv()

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

    # Write the response content to a local file
    with open("config.csv", "wb") as file:
        file.write(response.content)

    print("File downloaded successfully")
    read_config()


# Main execution logic
if __name__ == "__main__":
    nested_dictionaries = download_config()
