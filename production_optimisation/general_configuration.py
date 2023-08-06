
path_to_excel = "/Users/gebruiker/Dropbox/Werk/BMQSolutions/0_Production_optimisation/ElectroWatt_Optimisation.xlsx"

df_reader_helper = ['helper_read_sheets'] # Sheet that contains information about all the other sheets.
sheets_to_read = ['Orders_dataframe', 'Index_sets_dataframe', 'helper_read_sheets', 'Config_availability']

description_order_df = 'Description' # in cleaning the description columns of the orders dataframe should not be 'cleaned' that is turned to uppercase, because then the description might become unreadable.