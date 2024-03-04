import unittest

from vismod_processing import config_fetch

# Just an example test to show how it works
# Run with `hatch test`


class TestDriveDownload(unittest.TestCase):
    def test_csv_to_dict(self):
        with open("tests/data/drive_config.csv", "r") as file:
            csv_str = file.read()
            config = config_fetch.config_to_json(csv_str)

            self.assertIsInstance(config, dict)
            self.assertIn("Load Cells", config)
            self.assertIn("Wind Sensor", config)
            self.assertIn("Contact Info", config)
            self.assertIn("Last Modified", config)
