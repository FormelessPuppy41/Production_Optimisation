from general_configuration import path_to_excel
from data.data_reader import Data_Reader
from data.dataframe import Dataframe

import pandas as pd

#FIXME: Ask someone how to properly structure a package, such that relative imports work: what to put in __init__.py files.

path = path_to_excel
print(path)
sheets = ['Orders_dataframe', 'Sets_dataframe']

dataframes = Data_Reader('EW', path).read_all_dataframes(sheets)
for df in dataframes:
    if isinstance(df, pd.DataFrame):
        print(df)
    else:
        print(False)
    print(type(df))
