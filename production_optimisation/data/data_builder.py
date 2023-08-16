import pandas as pd
import math
from typing import List

from data.dataframe import Dataframe
from data.dataframes import Dataframes
from data.data_cleaner import Data_Cleaner
from data.data_index import Data_Index

from general_configuration import all_dataframes, data_builder_columns, data_indexes_columns

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

        self.index_df: Dataframe
        self.index_df_found = False
        self.index_df_enlarged = False

        self.excel_file = dataframes_class.get_dataframe_by_index(0).get_excel_file()

        orders_name = all_dataframes.get('orders_df')
        index_df_name = all_dataframes.get('index_sets_df')

        try: 
            self.orders_df = dataframes_class.get_dataframe_by_name(orders_name)
            self.orders_found = True
        except: 
            pass

        try: 
            self.index_df = dataframes_class.get_dataframe_by_name(index_df_name)
            self.index_df_found = True
        except: 
            pass
    
    
    def build_new_df_column_based(self, new_dataframe_name: str, data_builder_col: str):
        if self.orders_found:
            copy_orders_df = self.orders_df.create_copy_for_new_dataframe(new_dataframe_name)

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


    def build_penalty_df(self):
        dates_df = self.dataframes_class.get_dataframe_by_name(all_dataframes.get('dates_df')).get_pandas_dataframe()
        revenue_df = self.dataframes_class.get_dataframe_by_name(all_dataframes.get('revenue_df')).get_pandas_dataframe()
        time_req_df = self.dataframes_class.get_dataframe_by_name(all_dataframes.get('time_req_df')).get_pandas_dataframe()
        
        time_index = Data_Index(self.dataframes_class).get_index_set('time')
        orders_index = Data_Index(self.dataframes_class).get_orders_set()

        penalty_df = pd.DataFrame(index=time_index, columns=orders_index)

        for ti in time_index:
            for order in orders_index:
                penalty_df.loc[ti, order] = self.calc_penalty(ti=ti, order=order, dates_df=dates_df, revenue_df=revenue_df, time_req_df=time_req_df)

        penalty = Dataframe(self.excel_file, 'penalty', None)
        penalty.change_pandas_dataframe(penalty_df)

        self.dataframes_class.append_dataframe(penalty)


    @staticmethod
    def calc_penalty(ti:pd.Timestamp, order: str, dates_df: pd.DataFrame, revenue_df: pd.DataFrame, time_req_df: pd.DataFrame):
        date_start = dates_df.loc[order].iloc[0]
        date_deadline = dates_df.loc[order].iloc[1]
        revenue = revenue_df.loc[order].iloc[0]
        time_req_lb = time_req_df.loc[order].iloc[0]
        time_req_ub = time_req_df.loc[order].iloc[1]

        start_penalty = True if ti >= date_start else False
        penalty = 50

        if start_penalty:
            start_now = (ti-date_start)/pd.Timedelta('1D')
            deadline_now = (date_deadline - ti) / pd.Timedelta('1D')
            multiply_now = 4 * ((ti - pd.Timestamp('1900-01-01'))/ pd.Timedelta('1D'))
            exp_val = deadline_now/multiply_now
    
            penalty = start_now + math.exp(exp_val) + math.log(revenue)
        
        return penalty
    

    def build_complete_index_sets_df(self):
        if self.index_df_found and self.orders_found:
            indexer = Data_Index(self.dataframes_class)

            index_pandas_df = self.index_df.get_pandas_dataframe()
            orders_pandas_df = self.orders_df.get_pandas_dataframe()

            employee_line = indexer.get_index_set('employee')
            employee_line.extend(indexer.get_index_set('line'))
            order_suborder = orders_pandas_df.index.to_list()
            

            index_dict = {key: None for key in data_indexes_columns}

            for idx in index_dict.keys():
                try:
                    if indexer.get_index_set(idx) != []:
                        index_dict[idx] = indexer.get_index_set(idx)
                    else:
                        if idx == 'employee_line':
                            index_dict[idx] = employee_line
                        elif idx == 'order_suborder':
                         index_dict[idx] = order_suborder
                except:
                    print(f'{idx} not found in keys of index_dict: {index_dict.keys()}')

            self.index_df.change_pandas_dataframe(index_dict)

            self.index_df_enlarged = True
            
    def build_indicator(self, new_dataframe_name: str, data_builder_col: str):
        if self.orders_found:
            copy_orders_df = self.orders_df.create_copy_for_new_dataframe(new_dataframe_name)

            copy_orders_pandas_df = copy_orders_df.get_pandas_dataframe()

            keep_cols = data_builder_columns.get(data_builder_col)
            drop_cols = [col for col in copy_orders_pandas_df.columns if col not in keep_cols]

            new_pandas_dataframe = copy_orders_df.get_pandas_dataframe().drop(columns=drop_cols)

            for idx in new_pandas_dataframe.index:
                if new_pandas_dataframe.loc[idx].iloc[0] == 1 or new_pandas_dataframe.loc[idx].iloc[0] == True:
                    new_pandas_dataframe.loc[idx] = True
                else:
                    new_pandas_dataframe.loc[idx] = False

            copy_orders_df.change_pandas_dataframe(new_pandas_dataframe)

            new_dataframe = copy_orders_df
            self.dataframes_class.append_dataframe(new_dataframe)

            