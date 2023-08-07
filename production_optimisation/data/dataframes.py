import pandas as pd
from typing import List

from data.dataframe import Dataframe
from data.data_cleaner import Data_Cleaner


class Dataframes:
    """The Dataframes class stores a List of Dataframes. Using Dataframes one can easily clean all Dataframes or get a single Dataframe.
    """
    def __init__(self, dataframes: List[Dataframe]):
        """This is the constructor of Dataframes.

        Args:
            dataframes (List[Dataframe]): List of Dataframes.
        """
        self.dataframes: List[Dataframe] = dataframes


    def get_dataframe_by_name(self, dataframe_name: str) -> Dataframe:
        """Gets a single Dataframe from the Dataframes list based on the dataframe_name

        Args:
            dataframe_name (str): Name of the dataframe.

        Returns:
            Dataframe: Dataframe that is being called.
        """
        for df in self.dataframes:
            if dataframe_name == df.get_name_dataframe():
                return df
        
        raise KeyError(f'The given dataframe_name {dataframe_name} cannot be found in the dataframes {self.dataframes}')

    def get_dataframe_by_index(self, index: int) -> Dataframe:
        return self.dataframes[index]

    def clean_dataframes(self, df_helper_read_sheets: Dataframe):
        """Cleans all the Dataframes in the list of Dataframes.

        Args:
            df_helper_read_sheets (Dataframe): Helper df that contains all the sheets and corresponding sheettypes.
        """
        if not df_helper_read_sheets.get_cleaned_status():
            Data_Cleaner(df_helper_read_sheets).clean_helper_read_sheets_df()

        for df in self.dataframes:
                Data_Cleaner(df).clean_dfs(df_helper_read_sheets=df_helper_read_sheets)
    

    def append_dataframe(self, dataframe: Dataframe):
        """Adds a dataframe to the Dataframes list.

        Args:
            dataframe (Dataframe): Dataframe to add to the list.
        """
        self.dataframes.append(dataframe)