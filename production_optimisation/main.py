from general_configuration import path_to_excel
from data.data_reader import Data_Reader
from data.dataframe import Dataframe
from data.data_cleaner import Data_Cleaner

import pandas as pd

#FIXME: Ask someone how to properly structure a package, such that relative imports work: what to put in __init__.py files.

path = path_to_excel
sheets = ['Orders_dataframe', 'Index_sets_dataframe', 'helper_read_sheets']

read = Data_Reader('EW', path)
read.read_all_dataframes(sheets)

dataframes = read.get_dataframes()

orders_df = dataframes[0]
Data_Cleaner(orders_df).clean_order_df()

index_df = dataframes[1]
Data_Cleaner(index_df).clean_index_sets_df()

print()

print([dfs.get_pandas_dataframe() for dfs in dataframes])


#FIXME: Think about restructuring the classes, because why should dataframe be a subclass of excelfile, however it is handy to be ably to combine them
# But for that to be it is not necesarry for them to be parent en sub. After split it is easier to combine dataframe_cleaner and dataframe
# Then you can add a self.cleaned = 0 to the constructor => after cleaning the cleaned version gets stored. 

#TODO: 1 - which cleaning process: How to check that the inputted df is actually the lists df? \\
        # Perhaps creating a dictionary in excel which shows which file goes through which process.