from problem_declaration.models import EWOptimisation

from general_configuration import feasability_dfs

import pandas as pd

class SolvabilityTest:
    def __init__(self):
        pass
    
    class TestProblemFormulation(EWOptimisation):
        pass
    
    class TestManualPlanningEW(EWOptimisation):
        #FIXME: The check in 'Input PYTHON' in 'Handmatig Plannen' where 'Incompleet' is checked, could be added. But only after the reorginisation of 'data' because then you can add a instance variable that keeps a list of index combinations that have NaN values. 
        def __init__(self, ewOptimisation: EWOptimisation):
            self.dataframes_class = ewOptimisation.dataframes_class

            self.list_order_suborder = ewOptimisation.list_order_suborder
            self.list_time = ewOptimisation.list_time
            self.list_employee_line = ewOptimisation.list_employee_line
            self.list_employee = ewOptimisation.list_employee
            self.list_line = ewOptimisation.list_line

            self.orders_df = self.dataframes_class.get_dataframe_by_name('orders_df').get_pandas_dataframe().copy()
            self.manual_planning_df = self.dataframes_class.get_dataframe_by_name('manual_planning_df').get_pandas_dataframe().copy()
            self.availability_df = self.dataframes_class.get_dataframe_by_name('availability_df').get_pandas_dataframe().copy()
            self.specific_order_suborder_df = self.dataframes_class.get_dataframe_by_name('order_specific_df').get_pandas_dataframe().copy()
            self.skills_df = self.dataframes_class.get_dataframe_by_name('skills_df').get_pandas_dataframe().copy()

        
        def checkAll(self):
            self.checkAvailabilityForManualPlanning(self)
            self.checkSkillForManualPlanning(self)
            self.checkHoursPlannedPerEmpl_linePerTimeForManualPlanning(self)

        def checkManualPlanning(self):
            pass # find a way to combine the next functions into this one, such that they can only be called from this function.
            
        def checkAvailabilityForManualPlanning(self):
            empl_lineTime_help = self.manual_planning_df.copy().reset_index()
            
            group_cols = feasability_dfs.get('empl_line_vs_Time')[1]
            sum_col = feasability_dfs.get('empl_line_vs_Time')[2]
            empl_lineTime: pd.DataFrame = empl_lineTime_help.groupby(group_cols)[sum_col].sum()

            requirement_failed = False
            failed_combinations = []

            for idx in empl_lineTime.index:
                empl_line = idx[0]
                time = idx[1]
                if (empl_lineTime.loc[empl_line, time] >= 1).any():
                    if not empl_lineTime.loc[empl_line, time].iloc[0] == self.availability_df.loc[time, empl_line]:
                        requirement_failed = True
                        failed_combinations.append([empl_line, time])
            
            if requirement_failed == True:
                print('Availability restriciton not met in Manual_planning')
                print(f'The following combinations where the cause of the failed requirements: \n {failed_combinations}')
                raise ValueError(f'Available restriction not met in Manual_planning, the following combinations where the cause: {failed_combinations}')

        def checkSkillForManualPlanning(self):
            order_suborderEmpl_line_help = self.manual_planning_df.copy().reset_index()
            
            group_cols = feasability_dfs.get('order_suborder_vs_empl_line')[1]
            sum_col = feasability_dfs.get('order_suborder_vs_empl_line')[2]
            order_suborderEmpl_line: pd.DataFrame = order_suborderEmpl_line_help.groupby(group_cols)[sum_col].sum()

            specific_order = self.specific_order_suborder_df

            requirement_failed = False
            failed_combinations = []

            for idx in order_suborderEmpl_line.index:
                order_suborder = idx[0]
                empl_line = idx[1]
                suborder = specific_order.loc[order_suborder].iloc[1]

                if self.skills_df.loc[empl_line, suborder] == 0 and (order_suborderEmpl_line.loc[order_suborder, empl_line].iloc[0] >= 1).any():
                    requirement_failed = True
                    failed_combinations.append([order_suborder, suborder, empl_line])
            
            if requirement_failed == True:
                print('Skills restriciton not met in Manual_planning')
                print(f'The following combinations where the cause of the failed requirements: \n {failed_combinations}')
                raise ValueError(f'Skills restriction not met in Manual_planning, the following combinations where the cause: {failed_combinations}')

        def checkHoursPlannedPerEmpl_linePerTimeForManualPlanning(self):
            #FIXME: Double check also the first checker, there it is also used, perhaps there is an easy way to make this accessable in all checks. 
            empl_lineTime_help = self.manual_planning_df.copy().reset_index()
            
            group_cols = feasability_dfs.get('empl_line_vs_Time')[1]
            sum_col = feasability_dfs.get('empl_line_vs_Time')[2]
            empl_lineTime: pd.DataFrame = empl_lineTime_help.groupby(group_cols)[sum_col].sum()

            requirement_failed = False
            failed_combinations = []
            print(empl_lineTime)
            for idx in empl_lineTime.index:
                empl_line = idx[0]
                time = idx[1]
                if (empl_lineTime.loc[empl_line, time] > 1).any():
                    requirement_failed = True
                    failed_combinations.append([empl_line, time])
            
            if requirement_failed == True:
                print('Hours planned per empl_line at given moment restriciton is not met in Manual_planning')
                print(f'The following combinations where the cause of the failed requirements: \n {failed_combinations}')
                raise ValueError(f'Hours planned per empl_line at given moment restriction is not met in Manual_planning, the following combinations where the cause: {failed_combinations}')


                