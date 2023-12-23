import re
import pandas as pd

from data.data_process import Data_process
from problem_declaration.models import EWOptimisation
from problem_declaration.test_solvability import SolvabilityTest
from ganttChart.gantt_chart import GanttChart
from general_configuration import path_to_excel, time_limit

### FIND THE PATH AND EXCEL FILE TO READ DATA FROM.
patterns_to_search = ['.xlsx', '.xlsm']
patterns = '|'.join(re.escape(ext) for ext in patterns_to_search)

if re.search(patterns, path_to_excel):
    excel_file = pd.ExcelFile(path_to_excel)
    #excel_file_write = pd.ExcelFile(path_to_excel)
else:
    raise ValueError(f'No excel file found in directory {path_to_excel}')

### READ THE EXCEL FILE USING OPENPYXL.
excel_file = pd.ExcelFile(path_to_excel, engine='openpyxl')


### PROCESSING THE DATA.

# CREATE A DATA PROCESS
process = Data_process(excel_file) # add a way to check whether the data has changed in excel => store the data in database => no need to reread every time.
# READ THE HELPER SHEET OF THE EXCELFILE, THAT INDICATES WHICH SHEETS TO READ AND WHAT TYPE OF SHEET THEY ARE
process.process_helper_read_sheets('helper_read_sheets')
# READ ALL THE NECESARRY SHEETS BASED ON THEIR SHEET TYPE
process.process_read_dataframes()
# USING THE READ DATA, BUILD NEEDED DATAFRAMES
process.process_build_dataframes()
# CLOSE THE EXCELFILE
excel_file.close()

### BUILDING THE MATHEMATICAL MODEL FOR THE OPTIMISATION

# CREATE THE MODEL, GIVEN THE DATA
ewOpt = EWOptimisation(process.dataframes)
#process.dataframes.print_dataframes()
ewOpt.createModel()

# SOLVE THE MODEL
solv_test = SolvabilityTest().TestPlanningEW(ewOpt) 
#FIXME:FIXME:FIXME: The problem with the old/manual planning is that they cannot be preformed at the same time. This results in errors. So we have to find a way to sepearte them, such that they only get the allocation needed. 
#Also what if old and manual planning both have the same values, then the concat would result in a 2.0 value => out of bounds of binairy, so how to fix this. Or is this already checked via the hoursplannedperempllinepermoment requirement for oldjoinedmanual

# CHECK WHETHER THE INPUTTED DATA SATISFY THE CONTRAINTS
solv_test.checkAll()

# SOLVE THE ACTUAL MODEL
ewOpt.solve(solver_options={'timelimit': time_limit})
# EXPORT THE MODEL TO THE EXCELFILE
#ewOpt.export() # DO NOT EXPORT BEFORE BACKING UP THE EXCEL FILE

"""
### OBTAIN A USER INTERFACE FOR END USERS

# CREAT A GANTTCHART OBJECT FOR THE PRODUCTION SCHEDULE
gantt_chart = GanttChart(ewOpt.short_solution)
# CONVERT THE SOLUTION TO CORRECT FORMAT FOR THE GANTTCHART
gantt_chart.convert_dataframe(process.dataframes.get_dataframe_by_name('order_specific_df').get_pandas_dataframe())
# CREATE THE ACTUAL GANTTCHART
gantt_chart.create_ganttchart()
# SHOW THE GANTTCHART
gantt_chart.show_plt()
"""

#FIXME: ADD THE CORRECT OBJECTIVE FUNCTION: MINIMIZE GAPS ETC. FIXME
