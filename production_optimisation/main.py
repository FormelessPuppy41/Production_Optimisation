import re
import pandas as pd
from icecream import ic

from data.data_process import Data_process
from problem_declaration.models import EWOptimisation
from problem_declaration.test_solvability import SolvabilityTest
from ganttChart.gantt_chart import GanttChart
from general_configuration import path_to_excel, time_limit


def read():
    """Reading the data.

    Raises:
        ValueError: If there is no excel file found in the directory.

    Returns:
        pd.ExcelFile: The excelfile in a pd format.
    """
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

    return excel_file


def problem(dataProcess: Data_process):
    """Formulate the mathematical model

    Args:
        dataProcess (Data_process): Process containing the data.
    """
    ### BUILDING THE MATHEMATICAL MODEL FOR THE OPTIMISATION
    # CREATE THE MODEL, GIVEN THE DATA
    ewOpt = EWOptimisation(dataProcess.dataframes)
    #process.dataframes.print_dataframes()
    ewOpt.createModel()

    # SOLVE THE MODEL
    solv_test = SolvabilityTest().TestPlanningEW(ewOpt)

    # CHECK WHETHER THE INPUTTED DATA SATISFY THE CONTRAINTS
    solv_test.checkAll()


    # SOLVE THE ACTUAL MODEL
    ewOpt.solve(solver_options={'timelimit': time_limit})
    # EXPORT THE MODEL TO THE EXCELFILE
    #ewOpt.export() # DO NOT EXPORT BEFORE BACKING UP THE EXCEL FILE


def solution(ewOptimalisatie: EWOptimisation, dataProcess: Data_process):
    """Transform the solution into a ganttchart.

    Args:
        ewOptimalisatie (EWOptimisation): The mathematical model that has been solved
        dataProcess (Data_process): The dataprocess containing the data.
    """
    ### OBTAIN A USER INTERFACE FOR END USERS

    # CREAT A GANTTCHART OBJECT FOR THE PRODUCTION SCHEDULE
    gantt_chart = GanttChart(ewOptimalisatie.short_solution)
    # CONVERT THE SOLUTION TO CORRECT FORMAT FOR THE GANTTCHART
    gantt_chart.convert_dataframe(dataProcess.dataframes.get_dataframe_by_name('order_specific_df').get_pandas_dataframe())
    # CREATE THE ACTUAL GANTTCHART
    gantt_chart.create_ganttchart()
    # SHOW THE GANTTCHART
    gantt_chart.show_plt()


def main():
    """
    Read the data, process it and solve the mathematical model.
    """
    # Read the excel file
    excel_file = read()

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

    # Create, test and solve the problem.
    problem(process)



if __name__ == "__main__":
    main()