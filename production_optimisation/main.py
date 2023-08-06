from general_configuration import path_to_excel, df_reader_helper, all_dataframes
from data.data_reader import Data_Reader
from data.dataframe import Dataframe
from data.data_cleaner import Data_Cleaner
from data.data_getter import Dataframes

import pandas as pd

#FIXME: Ask someone how to properly structure a package, such that relative imports work: what to put in __init__.py files.

# Reading the helper_read_sheets: 'read1'
read1 = Data_Reader('EW_init', path_to_excel)

read1.read_all_dataframes(df_reader_helper)
dataframes_read1 = Dataframes(dataframes=read1.get_dataframes())

helper_read_dfs = all_dataframes.get('helper_read_dfs') # Change to input variable 'name_of_helper_read_dfs_in_Dictionary' when creating a function for this.
helper_read_sheets_df = dataframes_read1.get_dataframe_by_name(helper_read_dfs)

print(helper_read_sheets_df.get_pandas_dataframe())
dataframes_read1.clean_dataframes(helper_read_sheets_df)
print(helper_read_sheets_df.get_pandas_dataframe())

sheets_to_read = read1.get_sheets_to_read(helper_read_sheets_df)


print('******************')


# Reading all the informative sheets: 'read2'
# Needs helper_read_sheets_df from READ1
read2 = Data_Reader('EW', path_to_excel)

read2.read_all_dataframes(sheets_to_read)
dataframes = read2.get_dataframes()

for df in dataframes:
    Data_Cleaner(df).clean_dfs(helper_read_sheets_df)


print([dfs.get_pandas_dataframe() for dfs in dataframes])

dataframes_read2 = Dataframes(dataframes=dataframes)

