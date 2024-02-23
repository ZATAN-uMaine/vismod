from nptdms import TdmsFile
import pandas as pd
# from vismod_processing import syncConfig
import syncConfig

"""

"""


class Pre_Processor:
    def __init__(self, calibration_file_path):
        """
        Todo: calib_table should be initialized with Alex's function
        """
        self.calib_file_path = calibration_file_path
        # calib_file = pd.read_excel(calibration_file_path)
        self.calib_table = syncConfig.process_excel_to_dict(
            calibration_file_path
        )
        # calib_file.close()

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

    def add_calibs_from_local_xlsx(
        self, calib_table_path, calib_table_columns, index_column="WDAQ"
    ):
        """
        Takes a pair of excel-style string of column names (ex. 'L,H')
        One column is the calibration factors, the other is the index used
        Adds it to the self.calib_table dictionary.

        DO NOT USE, does not work with current format
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
        with TdmsFile.open(path) as tdms_file:
            for group in tdms_file.groups():
                tdms_dict = tdms_dict | {group.name: group.as_dataframe()}
        return pd.DataFrame.from_dict(tdms_dict)

    def get_local_data_as_dataframe(self, path):
        """
        Way simpler, just imports the whole file as a dataframe
        """
        with TdmsFile.open(path) as tdms_file:
            return tdms_file.as_dataframe()

    def apply_calibration(
        self,
        tdms_dict,
        fun=lambda item, config, sensor, channel: item
        * (config[sensor][channel]),
    ):
        """
        Just apply a given function 'fun' to calib valuesparameter
        This function has no side-efffects. It does rely on the calib table
        """

        for sensor in self.calib_table.keys():
            for channel in self.calib_table[sensor].keys():
                # This is a lazy, but necessary check
                # Calibs could use restructuring.
                if channel[-8:] == "Cable ID":
                    continue

                colname = f"/'{sensor}'/'{channel}'"
                tdms_dict[colname] = tdms_dict[colname].map(
                    lambda item: fun(item, self.calib_table, sensor, channel)
                )

        return tdms_dict

    def apply_calibration_map(
        self,
        remote_tdms_dict,
        colcodes="L,T",
        fun=lambda item, config, sensor, channel: item
        * config[sensor][channel],
    ):
        """
        Just apply a given function 'fun' to calib valuesparameter
        This is a pure function, it has no side-efffects. It does rely on the calib table
        """
        tdms_dict = remote_tdms_dict.copy()

        # Try-except just needed to handle the two import methods -temporary
        # try:
        #     for sensor in self.calib_table.keys():
        #         tdms_dict[sensor] = tdms_dict[sensor].map(
        #             lambda channel: map(
        #                 fun(
        #                     item,
        #                     self.calib_table,
        #                     sensor,
        #                     channel
        #                 ),
        #                 tdms_dict[sensor][channel]
        #             ),
        #             tdms_dict[sensor]
        #         )
        # except KeyError:
        #     tdms_dict = tdms_dict.map(
        #         lambda colname:
        #             map(
        #                 fun(
        #                     item,
        #                     self.calib_table,
        #                     colname.split('/')[0],
        #                     colname.split('/')[1]
        #                 ),
        #                 tdms_dict[colname]
        #             ),
        #     )
        return tdms_dict
