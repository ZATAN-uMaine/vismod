from nptdms import TdmsFile, ChannelObject
import pandas as pd

class CalibrationManager:
    def __init__(self, calibration_file_path, select_cols=None, select_index=None):
        self.calibration_file_path = calibration_file_path
        self.parameter_columns = select_cols
        self.calib_table = self.get_calibs_from_local_xlsx(select_cols, select_index)
        

    def rename_cols(self, new_dict):
        """
        Takes a dictionary mapping column names to new names
        Replaces column names of calib table
        """
        if type(new_dict) != dict():
            return
        self.calib_table.rename(
            columns = new_dict, 
            inplace=True
        )


    # Column names: 'L,H,R' index:'WDAQ'
    def get_calibs_from_local_xlsx(self, column_names, index):
        """
        Takes an excel-style string of column names (ex. 'A,H,R')
        => pandas data frame
        """
        table = pd.read_excel(self.calibration_file_path,  
                    usecols=column_names,
                    skiprows=4,
                    nrows=30,
                    index_col=index
                )
        table = table.iloc[2::2, :]
        indices = table.index.tolist()
        indices = list(map(lambda x: x.split()[0] + x.split()[1], indices))
        table.index  = indices

        #Rename columns to something actually sensible
        table.rename(
            columns = {'Cal Factor':'Load Cell', 'Cal Factor.1':'Temp Sensor'}, 
            inplace=True
        )
        return table
    

    def apply_calibration_factors(self, tdms_dict):
        for parameter in self.calib_table.columns:
            sensor = parameter.split('/')[0]
            channel = int(parameter.split('/')[1])
            tdms_dict[sensor][channel] = tdms_dict[sensor][channel].map(
                lambda f: f*self.calib_table[parameter][sensor+f'/{channel}']
            )
        return tdms_dict


class PreProcessor:
    def __init__(self, calibration_manager):
        self.calibration_manager = calibration_manager

    def set_manager(self, manager):
        self.calibration_manager = manager
        return

    def averageData(self, tdms_dict):
        return tdms_dict

    def calibrate_data(self, tdms_dict):
        return self.calibration_manager.apply_calibration_factors(tdms_dict)
 

    def calibrateData(self, tdms_dict):
        for sensor in tdms_dict:
            # Don't know if we need to process these, but they're shaped diff.
            # from the other load cells, so need to be processed seperately
            if sensor == 'FOS' or sensor == '14441':
                pass
            else:
                #Apply Calibration values to temperature values
                table = self.calibration_manager.calib_table
                tdms_dict[sensor]['TEMP'] = tdms_dict[sensor]['TEMP'].map(
                    lambda f: f*table['Temp Sensor'][sensor+'/1']
                )
                # Apply loadcell calibs
                tdms_dict[sensor]['ch1'] = tdms_dict[sensor]['ch1'].map(
                    lambda f: f*table['Load Cell'][sensor+'/1']
                )
                tdms_dict[sensor]['ch2'] = tdms_dict[sensor]['ch2'].map(
                    lambda f: f*table['Load Cell'][sensor+'/2']
                )

        return tdms_dict

    def get_local_data(self, path):
        """
        Takes an npTDMS object and the calib table
        => dictionary of pandas data frames
        """
        tdms_dict = {}
        indices = []
        with TdmsFile.open(path) as tdms_file:
            for group in tdms_file.groups():
                indices.append(group.name)
                tdms_dict = tdms_dict | {group.name:group.as_dataframe()}
        return tdms_dict

