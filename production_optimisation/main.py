import pulp
import re

from data.data_process import Data_process
from problem_declaration.models import EWOptimisation
from ganttChart.gantt_chart import GanttChart

from general_configuration import path_to_excel, time_limit

import pandas as pd

#FIXME: Ask someone how to properly structure a package, such that relative imports work: what to put in __init__.py files.


if re.search('.xlsx', path_to_excel):
    excel_file = pd.ExcelFile(path_to_excel)
else:
    raise ValueError(f'No excel file found in directory {path_to_excel}')

process = Data_process(excel_file)
process.process_helper_read_sheets('helper_read_sheets')
print(process.dataframes)
process.process_read_dataframes()
print(process.dataframes)
process.process_build_dataframes()
print(process.dataframes)

print(process.dataframes.get_dataframe_by_name('old_planning').get_pandas_dataframe())
ewOpt = EWOptimisation(process.dataframes)
ewOpt.createModel()
ewOpt.solve(solver_options={'timelimit': time_limit})

gantt_chart = GanttChart(ewOpt.short_solution)
gantt_chart.convert_dataframe()
gantt_chart.create_ganttchart()
gantt_chart.show_plt()

# write tests that check whether feasability is even possible

# Check combinations of order_suborder on a line, and whether lines can preform this suborder.
# Check whether there is enough timespan to plan all orders. That is per suborder, because if only lines work, then only lines suborders can be scheduled.
# Check that the inputted indexes are of the correct format, and give a message if they are not. 

# ADD: manual urgency in penalty.
# ADD: Constraint that minimizes amount of workers. But also a worker cannot work more than x hours per week. 

# Seperate the constraints into a class, and make functions that apply individual constraints, where multiple functions can be in one

# GANTCHART: line for start and deadline date, for each order a colour, and for each suborder a pattern?, dropdown filters for orders and emplys. scrollable?
