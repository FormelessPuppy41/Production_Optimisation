from general_configuration import path_to_excel
from data.excel_file import ExcelFile
from data.dataframe import Dataframe
from data.data_reader import Data_Reader

#FIXME: Ask someone how to properly structure a package, such that relative imports work: what to put in __init__.py files.

path = path_to_excel
print(path)
['Orders_dataframe']

dataframes = Data_Reader('EW', path).read_all_dataframes()
print(dataframes)