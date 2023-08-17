
path_to_excel = "/Users/gebruiker/Dropbox/Werk/BMQSolutions/0_Production_optimisation/ElectroWatt_Optimisation.xlsx"

df_reader_helper = ['helper_read_sheets'] # Sheet that contains information about all the other sheets. Possible to rename to 'sheet1', that way it is standardized, but also this is standardized as long as you dont change the name. 

sheet_types = { # Should be compatable with 'type of sheets' in 'config_main'
    'dont_read': 'df_dont_read', 
    'read': 'df_read', 
    'index_sets': 'df_sets_of_index', 
    'orders': 'df_orders', 
    'index_in_col_A': 'df_index1'
    }

description_order_df = 'Description' # in cleaning the 'description columns' of the orders_dataframe should not be 'cleaned' that is turned to uppercase, because then the description might become unreadable.

all_dataframes = { # 'in code name of dataframe': 'in stored dataframes name of dataframe'
    'helper_read_dfs': 'helper_read_sheets',
    'orders_df': 'Orders_dataframe',
    'index_sets_df': 'Index_sets_dataframe',
    'availability_df': 'Config_availability',
    'skills_df': 'Config_skills',
    'time_req_df': 'Time_required_per_order',
    'specific_line_df': 'Production_specific_line',
    'dates_df': 'dates_start_deadline',
    'suborders_df': 'Next_prev_suborder',
    'revenue_df': 'Revenue',
    'order_specific_df': 'Order_specific',
    'line_indicator': 'line_indicator',
    'penalty_df': 'penalty',
    'percentage_df': 'percentage'
} 

data_builder_columns = {
    'dates': ['Date_start', 'Date_deadline'],
    'time': ['Time_hours_lowerbound', 'Time_hours_upperbound'],
    'specific_line': ['Production_line_specific_line'],
    'next_prev_suborder': ['Previous_sub_order', 'Next_sub_order'], 
    'urgency': ['Manual_urgency'], # not in dataframes
    'percentage': ['Percentage_prev_sub_order_needed_before_next_sub_order'],
    'revenue': ['Revenue'],
    'specific_orders': ['Order_number', 'Sub_order'],
    'line_indicator': ['On_line']
}

dfs = { # Standard name: [ Name of excelsheet / dataframe, [ columns in (orders) dataframe]]
    'helper_read_dfs': ['helper_read_sheets', None], # read from excel
    'orders_df': ['Orders_dataframe', None], # read from excel
    'index_sets_df': ['Index_sets_dataframe', None], # read from excel
    'availability_df': ['Config_availability', None], # read from excel
    'skills_df': ['Config_skills', None], # read from excel
    'time_req_df': ['Time_required_per_order', ['Time_hours_lowerbound', 'Time_hours_upperbound']],
    'specific_line_df': ['Production_specific_line', ['Production_line_specific_line']],
    'dates_df': ['dates_start_deadline', ['Date_start', 'Date_deadline']],
    'next_prev_suborder_df': ['Next_prev_suborder', ['Previous_sub_order', 'Next_sub_order']],
    'revenue_df': ['Revenue', ['Revenue']],
    'order_specific_df': ['Order_specific', ['Order_number', 'Sub_order']],
    'line_indicator_df': ['line_indicator',  ['On_line']],
    'penalty_df': ['penalty', None], # build using other, already build, dataframes. 
    'percentage_df': ['percentage', ['Percentage_prev_sub_order_needed_before_next_sub_order']]
}

data_indexes_columns = { # Column titles of index_sets.
    'order_suborder': 'Orders_suborders',
    'order': 'Orders',
    'suborder': 'Sub_orders',
    'time': 'Time_intervals',
    'employee_line': 'Employee_line',
    'employee': 'Employees',
    'line': 'Production_lines'
}
#FIXME: Automate? use info of Dataframe, for example sheetname = str or none and/or dfname to fill this dictionary.
# combine them and leave some columns empty? Also possible to change it into a dataframe, or a dictionary with a list with different values:
# dict={order: [Orders_dataframe, [Previous_sub_order, Next_suborder], Orders], time: [.., [...], ...]}