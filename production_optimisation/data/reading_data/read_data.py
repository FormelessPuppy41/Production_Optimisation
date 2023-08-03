import pandas as pd
import openpyxl

#FIXME: Add a way to import the {path} from {general_configuration.py}.

#from production_optimisation.general_configuration import path_to_excel
#from general_configuration import path_to_excel
#path = path_to_excel

path = "/Users/gebruiker/Dropbox/Werk/BMQSolutions/0_Production_optimisation/ElectroWatt_Optimisation.xlsx"
xls = pd.ExcelFile(path)

sheet_names = xls.sheet_names

print(xls.sheet_names)
sheet_orders_df = sheet_names[1] # 'Orders_dataframe'
sheet_sets_df = sheet_names[2] # 'Sets_dataframe'

global orders_df
orders_df = pd.read_excel(
    io=path,
    sheet_name=sheet_orders_df
    ).fillna('')

global sets_df
sets_df = pd.read_excel(
    io=path,
    sheet_name=sheet_sets_df
).fillna('')

print(orders_df)
print()
print(sets_df)


