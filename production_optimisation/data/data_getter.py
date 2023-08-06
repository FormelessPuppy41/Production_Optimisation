import pandas as pd
from typing import List

from data.dataframe import Dataframe
from data.data_cleaner import Data_Cleaner


class Dataframes:
    def get_dataframes_to_read():
         pass

    def __init__(self, dataframes: List[Dataframe]):
        self.dataframes: List[Dataframe] = dataframes


    def get_dataframe_by_name(self, dataframe_name: str):
         for df in self.dataframes:
              if dataframe_name == df.get_name_dataframe():
                   return df


    def clean_dataframes(self, df_helper_read_sheets: Dataframe):
        if not df_helper_read_sheets.get_cleaned_status():
            Data_Cleaner(df_helper_read_sheets).clean_helper_read_sheets_df()

        for df in self.dataframes:
                Data_Cleaner(df).clean_dfs(df_helper_read_sheets=df_helper_read_sheets)
    

