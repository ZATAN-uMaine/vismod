from nptdms import TdmsFile
import pandas as pd


def get_calibs_from_xlsx(column_names):
    """
    Takes an excel-style string of column names (ex. 'A,H,R')
    => pandas data frame
    """
    table = pd.read_excel(
        "../raw-DAQ-files/sensorCalib.xlsx",
        usecols=column_names,
        skiprows=4,
        nrows=30,
        index_col="WDAQ",
    )
    table = table.iloc[2:26:2, :]
    indices = table.index.tolist()
    indices = list(map(lambda x: x.split()[0] + x.split()[1], indices))
    print(indices)
    table.index = indices  # I hate that this is the best I could come up with

    # Rename columns to something actually sensible
    table.rename(columns={"Cal Factor": "Load Cell"}, inplace=True)
    table.rename(columns={"Cal Factor.1": "Temp Sensor"}, inplace=True)

    return table


def get_calibrated_data(path, calib_table):
    """
    Takes an npTDMS object and the calib table
    => dictionary of pandas data frames
    """
    dic = {}
    indices = []
    with TdmsFile.open(path) as tdms_file:
        for group in tdms_file.groups():
            indices.append(group.name)
            dic = dic | {group.name: group.as_dataframe()}

    print(dic["45617"]["TEMP"])

    for sensor in dic:
        # Don't know if we need to process these, but they're shaped diff.
        # from the other load cells, so need to be processed seperately
        if sensor == "FOS" or sensor == "14441":
            pass
        else:
            # Apply Calibration values to temperature values
            dic[sensor]["TEMP"] = dic[sensor]["TEMP"].map(
                lambda f: f * calib_table["Temp Sensor"][sensor + "/1"]
            )
            # Apply loadcell calibs
            dic[sensor]["ch1"] = dic[sensor]["ch1"].map(
                lambda f: f * calib_table["Load Cell"][sensor + "/1"]
            )
            dic[sensor]["ch2"] = dic[sensor]["ch2"].map(
                lambda f: f * calib_table["Load Cell"][sensor + "/2"]
            )

    return dic


def main():
    # tdms_file = TdmsFile.read("../raw-DAQ-files/100123.tdms")
    calib_table = get_calibs_from_xlsx("L,H,R")
    print(calib_table)

    dic = get_calibrated_data("../raw-DAQ-files/100123.tdms", calib_table)
    print(dic)
    print(dic["45617"]["TEMP"])


if __name__ == "__main__":
    main()
