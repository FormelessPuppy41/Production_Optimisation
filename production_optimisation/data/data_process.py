from general_configuration import path_to_excel, df_reader_helper, all_dataframes, data_builder_columns
from data.data_reader import Data_Reader
from data.dataframe import Dataframe
from data.data_cleaner import Data_Cleaner
from data.dataframes import Dataframes
from data.data_builder import Data_Builder

import pandas as pd

#FIXME: Ask someone how to properly structure a package, such that relative imports work: what to put in __init__.py files.


class Data_process:
    def __init__(self, helper_read_dfs_name: str):
        self.helper_read_dfs_name = all_dataframes.get(helper_read_dfs_name)
        
        self.helper_read_sheets_df = None
        self.dataframes = None
        self.sheets_to_read = None


    def process_helper_read_sheets(self, name_reader: str):
        reader = Data_Reader(name_excel_file=name_reader, path_excel_file=path_to_excel)

        reader.read_all_dataframes(df_reader_helper)
        dataframes_reader = Dataframes(dataframes=reader.get_dataframes())

        self.helper_read_sheets_df = dataframes_reader.get_dataframe_by_name(self.helper_read_dfs_name)

        dataframes_reader.clean_dataframes(self.helper_read_sheets_df)
        self.sheets_to_read = reader.get_sheets_to_read(self.helper_read_sheets_df)


    def process_read_dataframes(self, name_reader: str):
        reader = Data_Reader(name_excel_file=name_reader, path_excel_file=path_to_excel)

        reader.read_all_dataframes(self.sheets_to_read)
        dataframes_reader = reader.get_dataframes()

        for df in dataframes_reader:
            Data_Cleaner(df).clean_dfs(self.helper_read_sheets_df)
        
        self.dataframes = Dataframes(dataframes=dataframes_reader)


    def process_build_dataframes(self):
        #FIXME: Dictionary: Create a dictionary that 'applies' both, then this can probably be moved to a 'build_all()' function, instead of calling individually.
        Data_Builder(self.dataframes).build_new_df_column_based(all_dataframes.get('time_req_df'), 'time') 
        Data_Builder(self.dataframes).build_new_df_column_based(all_dataframes.get('specific_line_df'), 'specific_line')
        Data_Builder(self.dataframes).build_new_df_column_based(all_dataframes.get('dates_df'), 'dates')
        Data_Builder(self.dataframes).build_new_df_column_based(all_dataframes.get('suborders_df'), 'next_prev_suborder')
        Data_Builder(self.dataframes).build_new_df_column_based(all_dataframes.get('revenue_df'), 'revenue')
        Data_Builder(self.dataframes).build_penalty_df()
        








