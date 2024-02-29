import unittest
import pandas as pd
import json

from vismod_processing.pre_processing import Pre_Processor


class TestPreProcessor(unittest.TestCase):
    def setUp(self):
        self.config = json.load(open("tests/data/example-config.json"))

        # Creating a Pre_Processor instance for testing
        self.pre_processor = Pre_Processor(self.config)

    @unittest.skip(
        "manually created data, might need reworking according to new format, good framework for a test though"
    )
    def test_apply_calibration(self):
        # Test applying calibration to sensor data
        tdms_dict = {
            "sensor1": {
                "ch1": pd.Series([1, 2, 3]),
                "ch2": pd.Series([4, 5, 6]),
            },
            "sensor2": {
                "ch1": pd.Series([7, 8, 9]),
                "ch2": pd.Series([10, 11, 12]),
            },
        }

        # Dummy calibration table
        calib_table = pd.DataFrame(
            {
                "sensor1/ch1": [1.1],
                "sensor1/ch2": [1.4],
                "sensor2/ch1": [1.7],
                "sensor2/ch2": [2.2],
            }
        )

        self.pre_processor.calib_table = calib_table

        tdms_dict = self.pre_processor.apply_calibration(tdms_dict)

        # Check if calibration has been applied correctly
        self.assertEqual(tdms_dict["sensor1"]["ch1"].iloc[1].item(), 1.1 * 2)

    def test_tdms_load(self):
        # fmt: off
        data = self.pre_processor.get_local_data_as_dataframe(
            "tests/data/081523.tdms"
        )
        # fmt: on

        self.assertIsInstance(data, pd.DataFrame)
        self.assertEqual(data.shape, (8640, 71))

    @unittest.skip("Need the correct calib function for this to work")
    def test_apply_calibration_integration(self):
        # test with new tdms method
        tdms_frame = self.pre_processor.get_local_data_as_dataframe(
            "tests/081523.tdms"
        )
        benchmark = self.pre_processor

        tdms_frame = self.pre_processor.apply_calibration(tdms_frame)
        self.assertEqual(
            self.benchmark["17AL-LC"][1], tdms_frame["/'43641'/'ch1'"].iloc[1]
        )

    def test_data_processing(self):
        self.pre_processor.load_and_process("tests/data/081523.tdms")
