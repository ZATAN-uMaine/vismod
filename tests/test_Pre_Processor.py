import unittest
import pandas as pd
import json

from vismod_processing.pre_processing import Pre_Processor

def csv_as_dataframe(filename):
    result = {}
    with open(filename, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            for key, value in row.items():
                if key not in result:
                    result[key] = []
                try:
                    result[key].append(float(value))
                except ValueError:
                    result[key].append(value)
    csvfile.close()
    return result

class TestPreProcessor(unittest.TestCase):
    def setUp(self):
        self.config = json.load(open("tests/data/example-config.json"))

        # Creating a Pre_Processor instance for testing
        self.pre_processor = Pre_Processor(self.config)

    @unittest.skip("Already know this works")
    def test_tdms_load(self):
        # fmt: off
        data = self.pre_processor.get_local_data_as_dataframe(
            "tests/data/081523.tdms"
        )
        # fmt: on
        self.assertIsInstance(data, pd.DataFrame)
        self.assertEqual(data.shape, (8640, 71))

    #@unittest.skip("Needs reworking according to new calib format")
    def test_apply_calibration(self):
        # Test applying calibration to sensor data. Test data created manually
        tdms_dict = pd.DataFrame({
                "43641-TIME":pd.Series([1, 2, 3,]),
                "43641-ch1": pd.Series([61, 72, 53,]),
                "43641-ch2": pd.Series([40, 50, 60,]),
                "43641-ch7": pd.Series([2.4, 1.5, 1.9,]),
                "43641-TEMP": pd.Series([80, 30, 190,]),
                "43644-TIME":pd.Series([1, 2, 3,]),
                "43644-ch1": pd.Series([70, 80, 90,]),
                "43644-ch2": pd.Series([10, 11, 12,]),
                "43644-ch7": pd.Series([1.24, 1.15, 1.99,]),
                "43644-TEMP": pd.Series([40, 50, 60,]),
                "14441-ch7" : pd.Series([0.2, 0.11, -0.12]),
                "14441-ch5" : pd.Series([0.2, 0.11, -0.12]),
                "14441-TEMP" : pd.Series([56, 43, 23]),
        })

        # Dummy calibration table
        calib_table = {
            "Load Cells": {
                "43641": {
                "1-Cal_Factor": 12.65,
                "1-Cable ID": "17A-Left",
                "1-TEMP": 98.86,
                "2-Cal_Factor": 12.604,
                "2-Cable ID": "17A-Right",
                "2-TEMP": 99.42643391521196
                },
                "43644": {
                "1-Cal_Factor": 12.55,
                "1-Cable ID": "10A-Left",
                "1-TEMP": 98.96039603960396,
                "2-Cal_Factor": 12.509,
                "2-Cable ID": "10A-Right",
                "2-TEMP": 99.15737298636928
                },
            },
            "Wind Sensor": {
                "Sensor ID": "14441"
            },
            "Contact Info": [
                "test@gmail.com",
                "test1@gmail.com"
            ],
            "Last Modified": "2024-02-23 23:57:41"
        }

        self.pre_processor.calib_table = calib_table

        tdms_dict = self.pre_processor.apply_calibration(tdms_dict)

        # Check if calibration has been applied correctly
        self.assertEqual(tdms_dict["17A-Left"].iloc[1].item(), 72 * 12.65 + 0)


    @unittest.skip("Need the correct calib function for this to work")
    def test_data_processing(self):
        benchmark = csv_as_dataframe("tests/data/081523-benchmark.csv")
        tdms_frame = self.pre_processor.load_and_process("tests/data/081523.tdms")

        self.assertEqual(
            self.benchmark["17AL-LC"][1], tdms_frame["17AL-LC"].iloc[1]
        )