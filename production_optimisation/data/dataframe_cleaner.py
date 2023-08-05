import pandas as pd

from data import data_helpers

# Make subclasses or 'sub'functions that call the functions in this class to clean them, 
# this way there is a distinction between different df's possible that require certain functions. 
# if you decide to make subfunction then this could be done in a new module named data_cleaning.py which imports this class
# and is called from data

class Dataframe_Cleaner:
    """The Dataframe_Cleaner class is for cleaning dataframes.
    """
    
    def __init__(self, pandas_df: pd.DataFrame):
        self.pandas_df = pandas_df


    def get_index_sets_from_dataframe(self):
        #TODO: 1 - which cleaning process: Only for the index dataframe.

        pd_df = self.pandas_df
        columns = pd_df.columns

        index_lists = []
        for col in columns:
            data_series = pd_df[col]
            data_list = data_series.to_list()

            cleaned_list = [data_helpers.clean_index_set_element(elem) for elem in data_list if elem]

            index_lists.append(cleaned_list)
        return index_lists
