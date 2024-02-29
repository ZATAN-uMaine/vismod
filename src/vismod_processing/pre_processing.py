from nptdms import TdmsFile
import pandas as pd
import json


def fix_tdms_col_name(name: str) -> str:
    splits = name.split("'")
    if len(splits) != 5:
        return name
    return f"{splits[1]}-{splits[3]}"


class Pre_Processor:
    """
    Takes both the calibration data and the latest sensor readings.
    Creates a frame with averaged data.
    """

    def __init__(self, calibration_dict):
        self.calib_table = calibration_dict
        self._check_calibration_dict()

    def _check_calibration_dict(self):
        """
        Does some sanity checks on the calibration table dictionary
        """
        assert isinstance(self.calib_table, dict)
        assert "Load Cells" in self.calib_table
        assert "Wind Sensor" in self.calib_table
        assert len(self.calib_table["Load Cells"].keys()) > 0

    def _check_tdms(self, tdms_data):
        for sensor in self.calib_table["Load Cells"].keys():
            assert f"{sensor}-TIME" in tdms_data
            assert f"{sensor}-TEMP" in tdms_data
            assert f"{sensor}-ch1" in tdms_data
            assert f"{sensor}-ch2" in tdms_data

    def get_local_data_as_dataframe(self, path):
        """
        Way simpler, just imports the whole file as a dataframe.
        Warning: kind of slow.
        """
        data = pd.DataFrame()
        with TdmsFile.open(path) as tdms_file:
            data = tdms_file.as_dataframe()

        # give the columns more sensible names
        data = data.rename(fix_tdms_col_name, axis="columns")
        self._check_tdms(data)
        return data

    def data_to_influx_shape(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.set_index("_time")
        return data

    def averageData(self, tdms_dict: pd.DataFrame):
        # average the data in 1hr buckets
        return tdms_dict.groupby(pd.Grouper(freq="30min")).mean()

    def calibrate_channel(channel, fun):
        """
        This will be a function that generalizes calibration
        `fun` would be a function/lambda that gets applied to a channel
        """
        return None

    def apply_calibration(
        self,
        tdms_dict,
    ) -> pd.DataFrame:
        """
        Creates new columns that apply correct callibration to strain sensors
        """

        results = pd.DataFrame()
        # all of the sensor time fields *should* be in sync
        results["_time"] = tdms_dict[
            f"{list(self.calib_table['Load Cells'].keys())[0]}-TIME"
        ]

        lcs = self.calib_table["Load Cells"]

        for sensor_id in lcs.keys():
            # temperature
            node_name = lcs[sensor_id]["1-Cable ID"].split("-")[0]
            results[f"{node_name}-TEMP"] = tdms_dict[f"{sensor_id}-TEMP"]

            # strain left
            cable_name1 = lcs[sensor_id]["1-Cable ID"]
            results[cable_name1] = (
                70
                - tdms_dict[f"{sensor_id}-ch1"] * lcs[sensor_id]["1-Cal_Factor"]
            )

            # strain right
            cable_name2 = lcs[sensor_id]["2-Cable ID"]
            results[cable_name2] = (
                70
                - tdms_dict[f"{sensor_id}-ch2"] * lcs[sensor_id]["2-Cal_Factor"]
            )

        external_sensor = self.calib_table["Wind Sensor"]["Sensor ID"]
        results["External-Wind-Speed"] = tdms_dict[f"{external_sensor}-ch7"]
        results["External-Wind-Direction"] = tdms_dict[
            f"{external_sensor}-ch5"
        ]  # noqa
        results["External-Temperature"] = tdms_dict[f"{external_sensor}-TEMP"]

        return results

    def load_and_process(self, data_path):
        """
        Call to process a data file once this class has been initialized
        """
        data = self.get_local_data_as_dataframe(data_path)
        data = self.apply_calibration(data)
        data = self.data_to_influx_shape(data)
        data = self.averageData(data)
        return data


# You need this boilerplate for scripts, otherwise you can't import it as a module without it running
if __name__ == "__main__":
    # Load the calibration data from data.json
    with open("src/vismod_processing/data.json", "r") as file:
        calibration_data = json.load(file)

    # Create a pre-processor object with the calibration data
    pre_processor = Pre_Processor(calibration_data)

    # Load and process the latest data file
    data_path = "tdms_files/022924.tdms"

    processed_data = pre_processor.load_and_process(data_path)
