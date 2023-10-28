import pulp
import re

from data.data_process import Data_process
from problem_declaration.models import EWOptimisation
from problem_declaration.test_solvability import SolvabilityTest
from ganttChart.gantt_chart import GanttChart

from general_configuration import path_to_excel, time_limit

import pandas as pd

#FIXME: Ask someone how to properly structure a package, such that relative imports work: what to put in __init__.py files.

patterns_to_search = ['.xlsx', '.xlsm']
patterns = '|'.join(re.escape(ext) for ext in patterns_to_search)

if re.search(patterns, path_to_excel):
    excel_file = pd.ExcelFile(path_to_excel)
    #excel_file_write = pd.ExcelFile(path_to_excel)
else:
    raise ValueError(f'No excel file found in directory {path_to_excel}')

excel_file = pd.ExcelFile(path_to_excel, engine='openpyxl')

process = Data_process(excel_file) # add a way to check whether the data has changed in excel => store the data in database => no need to reread every time.
process.process_helper_read_sheets('helper_read_sheets')
process.process_read_dataframes()
process.process_build_dataframes()

excel_file.close()
ewOpt = EWOptimisation(process.dataframes)
#process.dataframes.print_dataframes()
ewOpt.createModel()

solv_test = SolvabilityTest().TestPlanningEW(ewOpt) #FIXME:FIXME:FIXME: The problem with the old/manual planning is that they cannot be preformed at the same time. This results in errors. So we have to find a way to sepearte them, such that they only get the allocation needed. 
#Also what if old and manual planning both have the same values, then the concat would result in a 2.0 value => out of bounds of binairy, so how to fix this. Or is this already checked via the hoursplannedperempllinepermoment requirement for oldjoinedmanual
solv_test.checkAll()

ewOpt.solve(solver_options={'timelimit': time_limit})
#ewOpt.export() 


gantt_chart = GanttChart(ewOpt.short_solution)
gantt_chart.convert_dataframe(process.dataframes.get_dataframe_by_name('order_specific_df').get_pandas_dataframe())
gantt_chart.create_ganttchart()
gantt_chart.show_plt()

#FIXME: ADD THE CORRECT OBJECTIVE FUNCTION: MINIMIZE GAPS ETC. FIXME
#FIXME: How to add dynamic programming. First solve the schedule, then the allocation of people? max schedule per hour is max free people per hours (dynamicly calculated)

#FIXME: after adding the above, you can also implement senario modeling, by making it possible to add a single order and see when the best time to plan it is. That is the previous solution can be used, until the startdate of the new order, then recalculate and see the effect of accepting the new order. see the lecture 7 slides of air transportation pg.6/7/8/9

#TODO: From the erp system there is a solution for the planning, this can be used as a 'starting point' for solving. 






# Improve the dataclass: make subclasses for the different dataframes, that is, order_df gets it's own class within dataframe. Here all the unique features for example cleaning or reading rules can be specified, this way many of the modules can be 'removed' because they can be reorginazed into these subclasses.

# write tests that check whether feasability is even possible
# Check combinations of order_suborder on a line, and whether lines can preform this suborder.
# Check whether there is enough timespan to plan all orders. That is per suborder, because if only lines work, then only lines suborders can be scheduled.
# Check that the inputted indexes are of the correct format, and give a message if they are not. 
# Check: Lb and ub must be whole multliple of timespan of timeintervals.
# Check whether the order df is complete, that is the important columns are filled if not then 


# ADD: manual urgency in penalty. and minimize gaps, also minimize gaps between prev/next suborders. 
# ADD: Constraint that minimizes amount of workers. But also a worker cannot work more than x hours per week. 
# this might be possible by solving the 'subproblem' of allocation the workers on the orders, based on a penalty matrix for those workers, for example based on skills (needed for order) and cost per hour. 
# ADD: actual skill level on both orders and employees, because some workers can preform more difficult tasks than others.

# Seperate the constraints into a class, and make functions that apply individual constraints, where multiple functions can be in one

# GANTCHART: line for start and deadline date, for each order a colour, and for each suborder a pattern?, dropdown filters for orders and emplys. scrollable?
# GANTCHART: How to filter based on the order in a set/list? because not it is done alphabetically => mag mont, smd smd2 instead of mag smd smd2 mont, is already in solution_short in models.
# GANTCHART: Also add a chart that shows the individual schedules of employees. 

# ADDING VBA to automatically close and run the python optimisation and then reopening the excel file. 
# Aslo add a vba function that filters the manual input such that the orders are clustered, this way there is a better overview of all the manual inputs for orders. 

# Add a backreading of new start and end dates for the orders.
# ADD conditional formatting and search box for easily finding the different orders in a large list, look at stored vids on insta.
