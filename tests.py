import unittest
from preProcessing import CalibrationManager, PreProcessor

class TestCalibrationManager(unittest.TestCase):

    def setUp(self):
        self.temp_manager = CalibrationManager('calibTable.xlsx',
            select_cols='S,R',
            select_index='WDAQ'
        )
        self.loadcell_manager = CalibrationManager('calibTable.xlsx',
            select_cols='L,H',
            select_index='WDAQ'
        )
        self.pre_processor = PreProcessor(self.temp_manager

    def test_calibrate_data(self):
    

    def test_rename_cols(self):
    
    def test_get_calibs_from_xlsx(self):
        

class TestPreProcessor(unittest.TestCase):
    def setUp(self):
        # Optional: Set up any common objects or configurations needed for tests
        pass

    def test_set_calibration_manager(self):
        

    def test_average_data(self):
    

    def test_calibrate_data(self):
        



if __name__ == '__main__':
    
    pre_processor = PreProcessor(temp_manager)
    #pre_processor.get_local_data('')
    #pre_processor.

    
    pre_processor.set_manager(loadcell_manager)
    #pre_processor.get_local_data('')

    unittest.main()
