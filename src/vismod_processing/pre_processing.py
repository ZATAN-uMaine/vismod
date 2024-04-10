from nptdms import TdmsFile
import pandas as pd
import logging


def fix_tdms_col_name(name: str) -> str:
    """
    Fixes the column names from the tdms file
    """
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

        # Proper indexing for a key here is just group#-ch#
        self.tempCoeff = {
            "43641-1": 2.07,
            "43641-2": 2.98,
            "45617-1": 0.80,
            "45617-2": -0.58,
            "43644-1": 3.31,
            "43644-2": 2.49,
            "43643-1": -2.40,
            "43643-2": -1.37,
            "43642-1": 2.52,
            "43642-2": 1.25,
            "45616-1": -1.03,
            "45616-2": -0.34,
        }

    def _check_calibration_dict(self):
        """
        Does some sanity checks on the calibration table dictionary
        """
        assert isinstance(self.calib_table, dict)
        assert "Load Cells" in self.calib_table
        assert "Wind Sensor" in self.calib_table
        assert len(self.calib_table["Load Cells"].keys()) > 0

    def _check_tdms(self, tdms_data):
        """
        Does some sanity checks on the tdms data
        """
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

        # Fix the column names
        data = data.rename(fix_tdms_col_name, axis="columns")
        self._check_tdms(data)
        return data

    def averageData(self, tdms_dict: pd.DataFrame):
        """
        Average data into buckets.
        """
        # Average the data in 1hr buckets
        return tdms_dict.groupby(pd.Grouper(freq="2min")).mean()

    def loadcell_offset(self, temp, loadcell_id):
        """
        Returns the offset added to a loadcell if its outside
        the allowed temperature range between -30 and 140.
        Might be good to make this range a constant so its
        easily changed.
        """
        if temp > 140:
            return (140 - temp) * self.tempCoeff[loadcell_id]
        elif temp < -30:
            return (-30 - temp) * self.tempCoeff[loadcell_id]
        else:
            return 0

    def apply_calibration(
        self,
        tdms_dict,
    ) -> pd.DataFrame:
        """
        Creates a new dataframe with calibrated strain sensor readings
        and times in UTC
        """
        results = pd.DataFrame()
        lcs = self.calib_table["Load Cells"]

        # All of the sensor time fields *should* be in sync,
        # so just use the first one
        # _time is a datetime64[ns]
        results["_time"] = tdms_dict[f"{list(lcs.keys())[0]}-TIME"]
        # This will convert from Maine time to UTC. The `America/New_York`
        # timezone includes DST at this time:
        # https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
        # if Maine moves off of DST, this code will need to change
        results["_time"] = (
            results["_time"]
            .dt.tz_localize("America/New_York")
            .dt.tz_convert(None)
        )

        for sensor_id in lcs.keys():
            # Temperature
            node_name = lcs[sensor_id]["1-Cable ID"].split("-")[0]
            cal_factor = lcs[sensor_id]["1-Cal_Factor"]
            results[f"{node_name}-TEMP"] = tdms_dict[f"{sensor_id}-TEMP"]

            # Strain/load cells get calibrated by the equation:
            #           data * cal_factor + offset

            # strain left
            cable_name = lcs[sensor_id]["1-Cable ID"]
            strain = tdms_dict[f"{sensor_id}-ch1"]
            cal_factor = lcs[sensor_id]["1-Cal_Factor"]
            offset = tdms_dict[f"{sensor_id}-TEMP"].map(
                lambda element: self.loadcell_offset(element, f"{sensor_id}-1")
            )
            results[cable_name] = strain * cal_factor + offset

            # strain right
            cable_name = lcs[sensor_id]["2-Cable ID"]
            strain = tdms_dict[f"{sensor_id}-ch2"]
            cal_factor = lcs[sensor_id]["2-Cal_Factor"]
            offset = tdms_dict[f"{sensor_id}-TEMP"].map(
                lambda element: self.loadcell_offset(element, f"{sensor_id}-2")
            )
            results[cable_name] = strain * cal_factor + offset

        external_sensor = self.calib_table["Wind Sensor"]["Sensor ID"]
        results["External-Wind-Speed"] = tdms_dict[f"{external_sensor}-ch7"]
        results["External-Wind-Direction"] = tdms_dict[
            f"{external_sensor}-ch5"
        ]  # noqa
        results["External-Temperature"] = tdms_dict[f"{external_sensor}-TEMP"]

        return results

    def load_and_process(self, data_path):
        """
        Call to process a data file once this class has been initialized.
        Return None if the data file is invalid.
        """
        try:
            data = self.get_local_data_as_dataframe(data_path)
        except ValueError:
            logging.warn(
                f"TDMS file {data_path} appears to have invalid format."
            )
            return None
        except AssertionError:
            logging.warning("TDMS basic check failed")
            return None
        data = self.apply_calibration(data)
        data = data.set_index("_time")
        data = self.averageData(data)
        return data
