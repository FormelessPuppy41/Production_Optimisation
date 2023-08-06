from general_configuration import path_to_excel, sheets_to_read, df_reader_helper
from data.data_reader import Data_Reader
from data.dataframe import Dataframe
from data.data_cleaner import Data_Cleaner

import pandas as pd

#FIXME: Ask someone how to properly structure a package, such that relative imports work: what to put in __init__.py files.

# Reading the helper_read_sheets: 'read1'
read1 = Data_Reader('EW_init', path_to_excel)

read1.read_all_dataframes(df_reader_helper)
dataframes_read1 = read1.get_dataframes()

df_helper_read_sheets = dataframes_read1[0]
Data_Cleaner(df_helper_read_sheets).clean_helper_read_sheets_df()
print(df_helper_read_sheets.get_pandas_dataframe())

print('******************')

# Reading all the informative sheets: 'read2'
read2 = Data_Reader('EW', path_to_excel)

read2.read_all_dataframes(sheets_to_read)
dataframes = read2.get_dataframes()

orders_df = dataframes[0]
Data_Cleaner(orders_df).clean_order_df()

index_df = dataframes[1]
Data_Cleaner(index_df).clean_index_sets_df()

print()

print([dfs.get_pandas_dataframe() for dfs in dataframes])


#FIXME: Should data_cleaner and Dataframe_cleaner be combined? because now we get a lot op modules.

#TODO: 1 - which cleaning process: How to check that the inputted df is actually the lists df? \\
        # Perhaps creating a dictionary in excel which shows which file goes through which process.
