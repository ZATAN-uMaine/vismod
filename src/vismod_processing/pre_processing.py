from nptdms import TdmsFile
import pandas as pd

"""

"""


class Pre_Processor:
    def __init__(self, calibration_file_path):
        """
        This is just so we can have one pre_processor for each calibration table if we have multiple that
        need to be applied to the same data channels.
        """
        self.calib_file_path = calibration_file_path
        self.calib_table = pd.DataFrame()

    def get_calibs_from_local_csv(self, csv_path, index_column="WDAQ"):
        table = pd.read_csv(csv_path, index_col=index_column)

        # Parse the weird    space character out of the indices
        indices = table.index.tolist()
        indices = list(
            map(lambda label: label.split()[0] + label.split()[1], indices)
        )
        table.index = indices

        # Union with existing calb table
        self.calib_table = pd.concat([self.calib_table, table])

    def get_calibs_from_local_xlsx(
        self, calib_table_path, calib_table_columns, index_column="WDAQ"
    ):
        """
        Takes a pair of excel-style string of column names (ex. 'L,H')
        One column is the calibration factors, the other is the index we'll use
        Adds it to the self.calib_table dictionary.
        """
        table = pd.read_excel(
            calib_table_path,
            usecols=calib_table_columns,
            skiprows=4,
            nrows=30,
            index_col=index_column,
        )

        # Get every other row
        table = table.iloc[2::2, :]

        # Parse the weird    space character out of the indices
        indices = table.index.astype(str).tolist()
        indices = list(
            map(
                lambda label: (
                    (label.split()[0] + label.split()[1])
                    if len(label.split()) >= 2
                    else label
                ),
                indices,
            )
        )
        table.index = indices

        # Union with existing calb table
        self.calib_table = pd.concat([self.calib_table, table])

        """
        # Rename columns to something actually sensible, not generalizable.
        
        table.rename(
            columns={"Cal Factor": "Load Cell", "Cal Factor.1": "Temp Sensor"},
            inplace=True,
        )
        """
        return table

    def averageData(self, tdms_dict):
        return None

    def update_calib_table(self):
        return None

    def get_local_data(self, path):
        """
        (npTDMS object, path to calib-table)
        => dictionary of pandas data frames
        """
        tdms_dict = {}
        indices = []
        with TdmsFile.open(path) as tdms_file:
            for group in tdms_file.groups():
                indices.append(group.name)
                tdms_dict = tdms_dict | {group.name: group.as_dataframe()}
        return tdms_dict

    def get_local_data_as_dataframe(self, path):
        """
        Way simpler, just imports the whole file as a dataframe
        """
        with TdmsFile.open(path) as tdms_file:
            return tdms_file.as_dataframe()

    def apply_calibration(
        self,
        remote_tdms_dict,
        fun=lambda item, table, parameter, sensor, channel: item
        * table["Cal Factor"][sensor + f"/{channel}"],
    ):
        """
        Just apply a given function 'fun' to calib values
        Suggested: fun = lambda i, t, p, s, c: i * t[p][s + f"/{c}"]
        """
        tdms_dict = remote_tdms_dict.copy()

        for parameter in self.calib_table.columns:

            # For some reason it sometimes counts the colnames as a param.
            if len(parameter.split("/")) == 1:
                continue

            sensor = parameter.split("/")[0]
            channel = parameter.split("/")[1]

            # Temporary try-except, needed to handle the two ways we're importing
            try:
                tdms_dict[sensor][channel] = tdms_dict[sensor][channel].map(
                    lambda item: fun(
                        item, self.calib_table, parameter, sensor, channel
                    )
                )
            except KeyError:
                tdms_dict[f"/{sensor}/{channel}"] = tdms_dict[
                    f"/{sensor}/{channel}"
                ].map(
                    lambda item: fun(
                        item, self.calib_table, parameter, sensor, channel
                    )
                )
        return tdms_dict
