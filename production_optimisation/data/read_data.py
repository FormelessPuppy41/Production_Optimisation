import pandas as pd
import openpyxl
from ..general_configuration import path_to_excel

path = path_to_excel
xls = pd.ExcelFile(io=path, engine=["openpyxl"])

orders_df = pd.read_excel(io=path, sheet_name='Orders_dataframe')

print(orders_df) # Does not work from here, because this project is located on GitHub, not on my computer itself. 



