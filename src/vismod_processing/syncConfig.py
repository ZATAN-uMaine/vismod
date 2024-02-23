import pandas as pd
import json


def process_excel_to_dict(excel_file):
    # Read the Excel file
    df = pd.read_excel(excel_file, header=2)  # Column headers start at row 3

    # Extract contact info from Column A, skip unpopulated
    contact_info = df.iloc[4:, 0].dropna().tolist()

    # TODO move this to DB # Save contact info to a text file
    with open("contactinfo.txt", "w") as file:
        for info in contact_info:
            file.write(f"{info}\n")

    # Prepare dictionaries
    nested_dictionaries = {}
    for _, row in df.iloc[1:].iterrows():
        if pd.notna(row["Node"]):  # Check if column 'Node' is populated
            node = str(row["Node"])
            if node not in nested_dictionaries:
                nested_dictionaries[node] = {}  # Initialize a new dictionary

            dict_entry = {
                # Load cell calibration factor
                "Cal_Factor": row["Cal Factor_L"],
                # Cable ID is the label, row['Cable ID'] is the value
                "Cable ID": row["Cable ID"],
                # Since the TDMS files also use 'TEMP'
                # we will also use it here for consistency
                "TEMP": row["Cal Factor_T"],
            }

            # WDAQ channel number as key, 'Cal Factor' as value
            nested_dictionaries[node][row["WDAQ_L"]] = dict_entry

    # Convert dictionaries to JSON
    json_data = json.dumps(nested_dictionaries)

    # TODO move this to DB
    # Write JSON data to file
    with open("data.json", "w") as file:
        file.write(json_data)

    return nested_dictionaries


if __name__ == "__main__":
    # Adjust the path to the Excel file as necessary
    excel_file_path = "config.xlsx"

excel_file_path = "config.xlsx"
nested_dictionaries = process_excel_to_dict(excel_file_path)
# print(nested_dictionaries)
# Convert dictionaries to JSON
json_data = json.dumps(nested_dictionaries)

# TODO move this to DB
# Write JSON data to file
with open("data.json", "w") as file:
    file.write(json_data)
