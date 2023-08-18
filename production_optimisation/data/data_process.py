from general_configuration import df_reader_helper, dfs
from data.data_reader import Data_Reader
from data.dataframe import Dataframe
from data.data_cleaner import Data_Cleaner
from data.dataframes import Dataframes
from data.data_builder import Data_Builder
from data.data_index import Data_Index

import pandas as pd

from general_configuration import dfs_to_build_columnBased, dfs_to_build_indicatorBased
class Data_process:
    def __init__(self, pandas_excel_file: pd.ExcelFile):
        self.pandas_excel_file = pandas_excel_file
        self.helper_read_sheets_df = None
        self.dataframes = None
        self.sheets_to_read = None


    def process_helper_read_sheets(self, helper_read_dfs_name: str):
        reader = Data_Reader(pandas_excel_file=self.pandas_excel_file)

        self.helper_read_dfs_name = dfs.get(helper_read_dfs_name)[0]
        
        reader.read_all_dataframes(df_reader_helper)
        dataframes_reader = Dataframes(dataframes=reader.get_dataframes())

        self.helper_read_sheets_df = dataframes_reader.get_dataframe_by_name(self.helper_read_dfs_name)

        dataframes_reader.clean_dataframes(self.helper_read_sheets_df)
        self.sheets_to_read = reader.get_sheets_to_read(self.helper_read_sheets_df)


    def process_read_dataframes(self):
        reader = Data_Reader(pandas_excel_file=self.pandas_excel_file)

        reader.read_all_dataframes(self.sheets_to_read)
        dataframes_reader = reader.get_dataframes()

        for df in dataframes_reader:
            Data_Cleaner(df).clean_dfs(self.helper_read_sheets_df)
        
        self.dataframes = Dataframes(dataframes=dataframes_reader)


    def process_build_dataframes(self):
        builder = Data_Builder(self.dataframes)

        for df_name in dfs_to_build_columnBased:
            builder.build_new_df_column_based(dfs.get(df_name))

        builder.build_penalty_df()
        builder.build_complete_index_sets_df()

        for df_name in dfs_to_build_indicatorBased:
            builder.build_indicator(dfs.get(df_name))
        

    def process_get_index(self, index_set_type: str):
        return Data_Index(self.dataframes).get_index_set(index_set_type)
