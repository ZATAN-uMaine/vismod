import unittest
from vismod_processing.pre_processing import Pre_Processor
from vismod_processing import syncConfig
import pandas as pd
import csv


class TestPreProcessor(unittest.TestCase):
    def setUp(self):
        # Creating a Pre_Processor instance for testing
        self.pre_processor = Pre_Processor("tests/config.xlsx")

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
                        except ValueError:
                            result[key].append(value)
            csvfile.close()
            return result

        self.benchmark = parse_csv_columnwise(
            "tests/081523-Post-Processed-Ex.csv"
        )

    @unittest.skip("Old")
    def test_get_calibs_from_local_csv(self):
        # Test loading calibration data from CSV
        csv_path = "tests/sensorCalib.csv"
        self.pre_processor.get_calibs_from_local_csv(csv_path)
        self.assertIsInstance(self.pre_processor.calib_table, pd.DataFrame)
        # Add more assertions as needed

    @unittest.skip("Old")
    def test_get_calibs_from_local_xlsx(self):
        # Test loading calibration data from Excel
        xlsx_path = "tests/sensorCalib.xlsx"
        calib_table_columns = "L,H"
        self.pre_processor.get_calibs_from_local_xlsx(
            xlsx_path, calib_table_columns
        )
        self.assertIsInstance(self.pre_processor.calib_table, pd.DataFrame)
        # Add more assertions as needed

    def test_process_excel_to_dict(self):
        xlsx_path = "tests/config.xlsx"
        self.calib_table = syncConfig.process_excel_to_dict(xlsx_path)
        print(self.calib_table)
        self.assertEqual(self.calib_table["43641"]["ch2"], 12.604)

    def test_get_local_data_as_dataframe(self):
        # Test that simpler import function works

        tdms_frame = self.pre_processor.get_local_data_as_dataframe(
            "tests/081523.tdms"
        )
        self.assertEqual(71, len(tdms_frame.columns))
        # self.assertEqual(self.benchmark['17AL-LC'][1],
        #   tdms_frame["/'43641'/'ch1'"].iloc[1]
        # )

    def test_apply_calibration(self):
        # Test applying calibration to sensor data
        calib_table = pd.DataFrame(
            {
                "sensor1": {
                    "ch1": 1.1,
                    "ch2": 1.4,
                },
                "sensor2": {
                    "ch1": 1.7,
                    "ch2": 2.2,
                },
            }
        )

        # Dummy calibration table
        tdms_dict = pd.DataFrame(
            {
                "/'sensor1'/'ch1'": pd.Series([1, 2, 3, 9, 5, 13]),
                "/'sensor1'/'ch2'": pd.Series([4, 5, 6, 14, 0, 5]),
                "/'sensor2'/'ch1'": pd.Series([7, 8, 9, 9, 6, 11]),
                "/'sensor2'/'ch2'": pd.Series([10, 11, 12, 38, 7]),
            }
        )

        self.pre_processor.calib_table = calib_table

        # Testing whether custom lambda works
        def multiplier(item, table, sensor, channel):
            return 70 - (item * table[sensor][channel])

        tdms_dict = self.pre_processor.apply_calibration(
            tdms_dict, fun=multiplier
        )

        # Check if calibration has been applied correctly
        self.assertEqual(
            tdms_dict["/'sensor1'/'ch1'"].iloc[1].item(), 70 - (1.1 * 2)
        )

    # @unittest.skip("Need the correct calib function for this to work")
    def test_apply_calibration_integration(self):
        # test with new tdms method
        tdms_frame = self.pre_processor.get_local_data_as_dataframe(
            "tests/081523.tdms"
        )

        values_before = tdms_frame.copy()

        # self.pre_processor.get_calibs_from_local_csv("tests/sensorCalib.csv"
        tdms_frame = self.pre_processor.apply_calibration(tdms_frame)
        for i in range(1, 241):
            self.assertGreater(
                tdms_frame[f"/'43641'/'ch1'"].iloc[i],
                values_before[f"/'43641'/'ch1'"].iloc[i],
            )

            self.assertAlmostEqual(
                self.benchmark["17AL-LC"][i],
                tdms_frame[f"/'43641'/'ch1'"].iloc[i],
                places=-3,
            )
        # self.assertEqual(
        #     self.benchmark["17AL-LC"][1], tdms_frame[f"/'43641'/'ch1'"].iloc[1]
        # )


if __name__ == "__main__":
    import sys

    sys.path.insert(0, "/workspace/src/vismod_processing/")
    unittest.main()
