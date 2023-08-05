import pandas as pd

from data.dataframe_cleaner import Dataframe_Cleaner
from data.dataframe import Dataframe
from general_configuration import description_order_df

class Data_Cleaner:
    def __init__(self, dataframe: Dataframe):
        self.dataframe = dataframe
        self.pandas_df = self.dataframe.get_pandas_dataframe()

        self.cleaner = Dataframe_Cleaner(self.dataframe)

    def clean_index_sets_df(self):
        if not self.dataframe.get_cleaned_status():
            self.pandas_df = self.pandas_df.applymap(self.cleaner.clean_index_sets_elements)
    
            self.dataframe.change_pandas_dataframe(self.pandas_df)

        self.dataframe.change_status_to_cleaned()

        
    def clean_order_df(self):
        if not self.dataframe.get_cleaned_status():
            columns_to_clean = self.pandas_df.columns.drop(description_order_df)
            print(columns_to_clean)

            self.pandas_df = self.pandas_df.applymap(lambda x: self.cleaner.clean_orders_elements(x, columns_to_clean))
    
            self.dataframe.change_pandas_dataframe(self.pandas_df)

        self.dataframe.change_status_to_cleaned()
        
        