import unittest
import pandas as pd
import json

from vismod_processing.pre_processing import Pre_Processor


class TestPreProcessor(unittest.TestCase):
    def setUp(self):
        self.config = json.load(open("tests/data/example-config.json"))

        # Creating a Pre_Processor instance for testing
        self.pre_processor = Pre_Processor(self.config)

    def test_tdms_load(self):
        # fmt: off
        data = self.pre_processor.get_local_data_as_dataframe(
            "tests/data/081523.tdms"
        )
        # fmt: on

        self.assertIsInstance(data, pd.DataFrame)
        self.assertEqual(data.shape, (8640, 71))

    def test_data_processing(self):
        self.pre_processor.load_and_process("tests/data/081523.tdms")
