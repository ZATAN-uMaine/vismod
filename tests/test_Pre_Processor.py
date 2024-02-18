import unittest
from src.vismod_processing.pre_processing import Pre_Processor
import pandas as pd
import csv


class TestPreProcessor(unittest.TestCase):
    def setUp(self):
        # Creating a Pre_Processor instance for testing
        self.pre_processor = Pre_Processor("tests/sensorCalib.xlsx")

        def parse_csv_columnwise(filename):
            result = {}
            with open(filename, "r") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    for key, value in row.items():
                        if key not in result:
                            result[key] = []
                        try:
                            result[key].append(float(value))
                        except:
                            result[key].append(value)
            csvfile.close()
            return result

        self.benchmark = parse_csv_columnwise(
            "tests/081523-Post-Processed-Ex.csv"
        )

    def test_get_calibs_from_local_csv(self):
        # Test loading calibration data from CSV
        csv_path = "tests/sensorCalib.csv"
        self.pre_processor.get_calibs_from_local_csv(csv_path)
        self.assertIsInstance(self.pre_processor.calib_table, pd.DataFrame)
        # Add more assertions as needed

    def test_get_calibs_from_local_xlsx(self):
        # Test loading calibration data from Excel
        xlsx_path = "tests/sensorCalib.xlsx"
        calib_table_columns = "L,H"
        self.pre_processor.get_calibs_from_local_xlsx(
            xlsx_path, calib_table_columns
        )
        self.assertIsInstance(self.pre_processor.calib_table, pd.DataFrame)
        # Add more assertions as needed

    def test_get_local_data_as_dataframe(self):
        # Test that simpler import function works

        tdms_frame = self.pre_processor.get_local_data_as_dataframe(
            "tests/081523.tdms"
        )
        self.assertEqual(71, len(tdms_frame.columns))
        # self.assertEqual(self.benchmark['17AL-LC'][1], tdms_frame["/'43641'/'ch1'"].iloc[1])

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

        # Testing whether custom lambda works
        def multiplier(item, table, parameter, sensor, channel):
            return item * table[sensor + f"/{channel}"]

        tdms_dict = self.pre_processor.apply_calibration(
            tdms_dict, fun=multiplier
        )

        # Check if calibration has been applied correctly
        self.assertEqual(tdms_dict["sensor1"]["ch1"].iloc[1].item(), 1.1 * 2)

    def test_apply_calibration_integration(self):
        # test with new tdms method
        tdms_frame = self.pre_processor.get_local_data_as_dataframe(
            "tests/081523.tdms"
        )
        calib_table = self.pre_processor.get_calibs_from_local_csv(
            "tests/sensorCalib.csv"
        )

        tdms_frame = self.pre_processor.apply_calibration(tdms_frame)
        print(tdms_frame)
        # self.assertEqual(tdms_dict[''], 1.1 * 2)


if __name__ == "__main__":
    unittest.main()
