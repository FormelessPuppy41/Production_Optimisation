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

process = Data_process(excel_file)
process.process_helper_read_sheets('helper_read_sheets')
process.process_read_dataframes()
process.process_build_dataframes()

excel_file.close()
ewOpt = EWOptimisation(process.dataframes)
#process.dataframes.print_dataframes()
ewOpt.createModel()

solv_test = SolvabilityTest().TestManualPlanningEW(ewOpt)
solv_test.checkAll()

"""ewOpt.solve(solver_options={'timelimit': time_limit})
#ewOpt.export() 


gantt_chart = GanttChart(ewOpt.short_solution)
gantt_chart.convert_dataframe()
gantt_chart.create_ganttchart()
gantt_chart.show_plt()"""

# Improve the dataclass: make subclasses for the different dataframes, that is, order_df gets it's own class within dataframe. Here all the unique features for example cleaning or reading rules can be specified, this way many of the modules can be 'removed' because they can be reorginazed into these subclasses.

# write tests that check whether feasability is even possible
# Check combinations of order_suborder on a line, and whether lines can preform this suborder.
# Check whether there is enough timespan to plan all orders. That is per suborder, because if only lines work, then only lines suborders can be scheduled.
# Check that the inputted indexes are of the correct format, and give a message if they are not. 
# Check: Lb and ub must be whole multliple of timespan of timeintervals.


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
