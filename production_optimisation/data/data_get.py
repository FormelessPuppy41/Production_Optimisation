import pandas as pd

from data import data_helpers
from data.dataframe import Dataframe


class Dataframe_Get:
    def get_dataframes_to_read():
         pass

    def __init__(self, dataframe: Dataframe):
        self.dataframe = dataframe,
        self.pandas_dataframe = dataframe.get_pandas_dataframe()







    def get_index_sets_from_dataframe(self):
            pd_df = self.pandas_df
            columns = pd_df.columns

            index_lists = []
            for col in columns:
                data_series = pd_df[col]
                data_list = data_series.to_list()

                cleaned_list = [data_helpers.clean_index_set_element(elem) for elem in data_list if elem]

                index_lists.append(cleaned_list)
            return index_lists