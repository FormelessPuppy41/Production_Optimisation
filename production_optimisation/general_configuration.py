# Dependencies: Pandas, Pyomo, xlsxwriter, openpyxl

path_to_excel = '/Users/gebruiker/Documents/GitHub/Production_Optimisation/production_optimisation/EW_Optimisation.xlsm'

#"/Users/gebruiker/Dropbox/Werk/BMQSolutions/0_Production_optimisation/ElectroWatt_Optimisation.xlsx"
time_limit = 60
old_planning_limit = '21-08-2023 14:00:00' # format is important, see the format in the olplanning constraint.

df_reader_helper = ['helper_read_sheets'] # Sheet that contains information about all the other sheets. Possible to rename to 'sheet1', that way it is standardized, but also this is standardized as long as you dont change the name. 

sheet_types = { # Should be compatable with 'type of sheets' in 'config_main'
    'dont_read': 'df_dont_read', 
    'read': 'df_read', 
    'index_sets': 'df_sets_of_index', 
    'orders': 'df_orders', 
    'index_in_col_A': 'df_index1',
    'planning': 'df_planning',
    'manual_planning': 'df_manual_planning'
}

description_order_df = 'Description' # in cleaning the 'description columns' of the orders_dataframe should not be 'cleaned' that is turned to uppercase, because then the description might become unreadable.

dfs = { # Standard name: [ Name of excelsheet / dataframe, [ columns in (orders) dataframe], 'filter_type']
    'helper_read_sheets': ['helper_read_sheets', None, ''], # read from excel
    'orders_df': ['Orders_dataframe', None, ''], # read from excel
    'index_sets_df': ['Index_sets_dataframe', None, ''], # read from excel
    'availability_df': ['Config_availability', None, 0.0], # read from excel
    'skills_df': ['Config_skills', None, 0.0], # read from excel
    'old_planning_df':['Planning', None, 0.0], # read from excel
    'manual_planning_df':['Manual_planning', None, 0.0], # read from excel
    'time_req_df': ['Time_required_per_order', ['Time_hours_lowerbound', 'Time_hours_upperbound'], None],
    'specific_line_df': ['Production_specific_line', ['Production_line_specific_line'], None],
    'dates_df': ['dates_start_deadline', ['Date_start', 'Date_deadline'], None],
    'next_prev_suborder_df': ['Next_prev_suborder', ['Previous_sub_order', 'Next_sub_order'], None],
    'revenue_df': ['Revenue', ['Revenue'], None],
    'order_specific_df': ['Order_specific', ['Order_number', 'Sub_order'], None],
    'line_indicator_df': ['line_indicator',  ['On_line'], None],
    'penalty_df': ['penalty', None, None], # build using other, already build, dataframes. 
    'old_and_manual_planning_df': ['old_and_manual_planning_df', None, None],
    'percentage_df': ['percentage', ['Percentage_prev_sub_order_needed_before_next_sub_order'], None],
    'solution_df': ['Planning', None, 0.0] # TO EXCEL, so first entry is sheet to write to. 
} #FIXME: Split up in different dictionaries for different functions, this is unorganised. make dict for read excel, dict for build, dict for test_validation.
# Also add an example input like in Feasability_dfs

feasability_dfs = {
    'EXAMPLE': ['EXAMPLEN_NAME', ['COLUMNS_THAT_BUILDS_DF'], ['SUM_LEAVE_COLUMNS/SUM_OVER_ALL_COLS_EXCEPT..']],
    'empl_line_vs_Time': ['empl_line_vs_Time', ['empl_line', 'time'], ['allocation']],
    'order_suborder_vs_empl_line': ['order_suborder_vs_empl_line', ['order_suborder', 'empl_line'], ['allocation']], 
    'order_suborder_vs_allocation': ['order_suborder_vs_allocation', ['order_suborder'], ['allocation']]
}

dfs_to_build_columnBased = ['time_req_df', 'specific_line_df', 'dates_df', 'next_prev_suborder_df', 'revenue_df', 'order_specific_df', 'percentage_df'] # From orders_df. Strings should be from 'dfs'.
dfs_to_build_indicatorBased = ['line_indicator_df'] # Strings should be from 'dfs'. 
#FIXME: These could be removed if the previous fixme about differen dictionaries for the dfs {} is completed. 

data_indexes_columns = { # Column titles of index_sets.
    'order_suborder': 'Orders_suborders',
    'order': 'Orders',
    'suborder': 'Sub_orders',
    'time': 'Time_intervals',
    'employee_line': 'Employee_line',
    'employee': 'Employees',
    'line': 'Production_lines'
}
