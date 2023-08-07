import pandas as pd
import math
from typing import List

from data.dataframe import Dataframe
from data.dataframes import Dataframes
from data.data_cleaner import Data_Cleaner
from general_configuration import all_dataframes, data_builder_columns

class Data_Builder:
    def __init__(self, dataframes_class: Dataframes):
        """Constructor of the Data_Cuilder class

        Args:
            dataframes_class (Dataframes): All the dataframes to build from and add new dataframes to.
        """
        self.dataframes_class = dataframes_class
        self.dataframes = dataframes_class.dataframes
        self.orders_df: Dataframe
        self.orders_found = False
        self.excel_file = dataframes_class.get_dataframe_by_index(0).get_excel_file()

        orders_name = all_dataframes.get('orders_df')

        try: 
            self.orders_df = dataframes_class.get_dataframe_by_name(orders_name)
            self.orders_found = True
        except: 
            pass
    
    
    def build_new_df_column_based(self, new_dataframe_name: str, data_builder_col: str):
        if self.orders_found:
            copy_orders_df = self.orders_df.create_copy_for_new_dataframe(new_dataframe_name)
            Data_Cleaner(copy_orders_df).change_df_index_to_one() #FIXME: orders index.

            copy_orders_pandas_df = copy_orders_df.get_pandas_dataframe()

            keep_cols = data_builder_columns.get(data_builder_col)
            drop_cols = [col for col in copy_orders_pandas_df.columns if col not in keep_cols]

            new_pandas_dataframe = copy_orders_df.get_pandas_dataframe().drop(columns=drop_cols)

            copy_orders_df.change_pandas_dataframe(new_pandas_dataframe)

            new_dataframe = copy_orders_df
            self.dataframes_class.append_dataframe(new_dataframe)


    def build_old_planning_df(self, column_names: str):
        pass
    def build_manual_planning_df(self, column_names: str):
        pass
    def build_old_or_manual_planning_df(self, columns_names: str):
        pass

    def build_to_calculate_order_df(self, column_names: str): # probably not nessecary.
        pass

    def build_dates_start_deadline_df(self, columns_names: str):
        pass
    def build_specific_production_line_df(self, columns_names: str):
        pass
    def build_time_required_per_order_df(self, column_names: List[str]):
        pass
    def build_next_and_prev_suborder_df(self, columm_names: str):
        pass
    def build_revenue_df(self,column_names: str):
        pass

    def build_penalty_df(self, column_names: str):
        dates_df = self.dataframes_class.get_dataframe_by_name('dates_df').get_pandas_dataframe()
        revenue_df = self.dataframes_class.get_dataframe_by_name('revenue_df').get_pandas_dataframe()
        time_req_df = self.dataframes_class.get_dataframe_by_name('time_req_df').get_pandas_dataframe()
        
        #see excel. penalty function.
        