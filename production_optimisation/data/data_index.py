from data.dataframe import Dataframe
from data.dataframes import Dataframes
from general_configuration import all_dataframes, data_indexes_columns

class Data_Index(Dataframes):
    def __init__(self, dataframes: Dataframes):
        self.dataframes = dataframes

        index_df_name = all_dataframes.get('index_sets_df')
        orders_df_name = all_dataframes.get('orders_df')
        try:
            self.index_df = self.dataframes.get_dataframe_by_name(index_df_name)
            self.orders_df = self.dataframes.get_dataframe_by_name(orders_df_name)
        except:
            KeyError(f' {index_df_name} or {orders_df_name} could not be found in the given dataframes: {self.dataframes}')


    def get_index_set(self, index_set_type: str):
        index_set_name = data_indexes_columns.get(index_set_type)
        index_set = self.index_df.get_pandas_dataframe()[index_set_name].to_list()
        index_set = [idx for idx in index_set if idx != '']
        return index_set
    

    def get_orders_set(self):
        return self.orders_df.get_pandas_dataframe().index.to_list()
        


