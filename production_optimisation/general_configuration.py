
path_to_excel = "/Users/gebruiker/Dropbox/Werk/BMQSolutions/0_Production_optimisation/ElectroWatt_Optimisation.xlsx"

df_reader_helper = ['helper_read_sheets'] # Sheet that contains information about all the other sheets. Possible to rename to 'sheet1', that way it is standardized, but also this is standardized as long as you dont change the name. 

sheet_types = {'dont_read': 'df_dont_read', 
               'read': 'df_read', 
               'index_sets': 'df_sets_of_index', 
               'orders': 'df_orders', 
               'index_in_col_A': 'df_index1'
               }

description_order_df = 'Description' # in cleaning the description columns of the orders dataframe should not be 'cleaned' that is turned to uppercase, because then the description might become unreadable.


all_dataframes = {
    'helper_read_dfs': 'helper_read_sheets',
    'Orders_df': 'Orders_dataframe',
    'Index_sets_df': 'Index_sets_dataframe',
    'availability_df': 'Config_availability',
    'skills_df': 'Config_skills',
} #FIXME: Automate? use info of Dataframe, for example sheetname = str or none and/or dfname to fill this dictionary.