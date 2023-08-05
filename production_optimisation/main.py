from general_configuration import path_to_excel
from data.data_reader import Data_Reader
from data.dataframe import Dataframe
from data.dataframe_cleaner import Dataframe_Cleaner

import pandas as pd

#FIXME: Ask someone how to properly structure a package, such that relative imports work: what to put in __init__.py files.

path = path_to_excel
sheets = ['Orders_dataframe', 'Index_sets_dataframe']

dataframes = Data_Reader('EW', path).read_all_dataframes(sheets)

index_df = dataframes[1]
cleaned_index_df = Dataframe_Cleaner(index_df).get_index_sets_from_dataframe()
print(cleaned_index_df)




#TODO: 1 - which cleaning process: How to check that the inputted df is actually the lists df? \\
        # Perhaps creating a dictionary in excel which shows which file goes through which process.