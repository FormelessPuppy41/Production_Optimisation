from problem_declaration.models import EWOptimisation

from general_configuration import feasability_dfs

import pandas as pd

class SolvabilityTest:
    def __init__(self):
        pass
    
    class TestProblemFormulation(EWOptimisation):
        pass
    
    class TestPlanningEW(EWOptimisation):
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
            self.old_planning_df = self.dataframes_class.get_dataframe_by_name('old_planning_df').get_pandas_dataframe().copy()
            self.availability_df = self.dataframes_class.get_dataframe_by_name('availability_df').get_pandas_dataframe().copy()
            self.specific_order_suborder_df = self.dataframes_class.get_dataframe_by_name('order_specific_df').get_pandas_dataframe().copy()
            self.skills_df = self.dataframes_class.get_dataframe_by_name('skills_df').get_pandas_dataframe().copy()
            self.required_hours_df = self.dataframes_class.get_dataframe_by_name('time_req_df').get_pandas_dataframe().copy()
            self.specific_production_line = self.dataframes_class.get_dataframe_by_name('specific_line_df').get_pandas_dataframe().copy()

        
        def checkAll(self): #TODO: it is possible to combine all errors into one big message, this way users see all possible errors at the same time.
            if not self.checkOldJOINEDManualPlanning():
                self.checkManualPlanning()
                self.checkOldPlanning()

        def checkManualPlanning(self):
            planning = self.manual_planning_df
            name_planning = 'Manual Planning'

            self.check_planning_restrictions(planning_df=planning, name_planning=name_planning)
            
        def checkOldPlanning(self):
            planning = self.old_planning_df
            name_planning = 'Old Planning'

            self.check_planning_restrictions(planning_df=planning, name_planning=name_planning)

        def checkOldJOINEDManualPlanning(self):
            if not self.old_planning_df.empty and not self.manual_planning_df.empty:
                planning = pd.concat([self.old_planning_df, self.manual_planning_df])
            elif not self.old_planning_df.empty and self.manual_planning_df.empty:
                planning = self.old_planning_df
            elif self.old_planning_df.empty and not self.manual_planning_df.empty:
                planning = self.manual_planning_df
            else:
                planning = pd.DataFrame
            
            name_planning = 'Old AND/OR Manual planning'

            self.check_planning_restrictions(planning_df=planning, name_planning=name_planning) 

        def check_planning_restrictions(self, planning_df: pd.DataFrame, name_planning: str):
            if not planning_df.empty:
                self.checkAvailabilityForPlanning(planning_df=planning_df, name_planning=name_planning)
                self.checkSkillForPlanning(planning_df=planning_df, name_planning=name_planning)
                self.checkHoursPlannedPerEmpl_linePerTimeForPlanning(planning_df=planning_df, name_planning=name_planning)
                self.checkRequiredHoursPlannedUpperboundForPlanning(planning_df=planning_df, name_planning=name_planning)
                self.checkSpecificLinesForPlanning(planning_df=planning_df, name_planning=name_planning)

        def checkAvailabilityForPlanning(self, planning_df: pd.DataFrame, name_planning: str):
            empl_lineTime_help = planning_df.copy().reset_index()
            
            group_cols = feasability_dfs.get('empl_line_vs_Time')[1]
            sum_col = feasability_dfs.get('empl_line_vs_Time')[2]
            empl_lineTime: pd.DataFrame = empl_lineTime_help.groupby(group_cols)[sum_col].sum() #FIXME: Possibly do this in the cleaning? except if in other checks the sum is not needed, but the normal version.
            
            requirement_failed = False
            failed_combinations = []

            for idx in empl_lineTime.index:
                empl_line = idx[0]
                time = idx[1]
                if (empl_lineTime.loc[empl_line, time] >= 1).any():
                    if not empl_lineTime.loc[empl_line, time].iloc[0] >= self.availability_df.loc[time, empl_line]:
                        requirement_failed = True
                        failed_combinations.append([empl_line, time])
            
            if requirement_failed == True:
                print(f'"Empl_line should be available when planned" restriciton not met in {name_planning}')
                print(f'The following combinations where the cause of the failed requirements: \n {failed_combinations}')
                print('This means that for the above combinations, the planned employee or line is not available at the given time.')
                raise ValueError(f'"Empl_line should be available when planned" restriction not met in {name_planning}, the following combinations where the cause: {failed_combinations}. This means that for the above combinations, the planned employee or line is not available at the given time.')

        def checkSkillForPlanning(self, planning_df: pd.DataFrame, name_planning: str):
            order_suborderEmpl_line_help = planning_df.copy().reset_index()
            
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
                print(f'"Empl_line should posses skills for planned suborder" restriciton not met in {name_planning}')
                print(f'The following combinations where the cause of the failed requirements: \n {failed_combinations}')
                print('This means that an employee is planned more than ones at a given moment. This could be due to being planned twice, once in manual_planning and once in the old_planning')
                raise ValueError(f'"Empl_line should posses skills for planned suborder" restriction not met in {name_planning}, the following combinations where the cause: {failed_combinations}')

        def checkHoursPlannedPerEmpl_linePerTimeForPlanning(self, planning_df: pd.DataFrame, name_planning: str):
            #FIXME: Double check also the first checker, there it is also used, perhaps there is an easy way to make this accessable in all checks. 
            empl_lineTime_help = planning_df.copy().reset_index()
            
            group_cols = feasability_dfs.get('empl_line_vs_Time')[1]
            sum_col = feasability_dfs.get('empl_line_vs_Time')[2]
            empl_lineTime: pd.DataFrame = empl_lineTime_help.groupby(group_cols)[sum_col].sum()

            requirement_failed = False
            failed_combinations = []
            
            for idx in empl_lineTime.index:
                empl_line = idx[0]
                time = idx[1]
                if (empl_lineTime.loc[empl_line, time] > 1).any(): #FIXME: It is possible to change this, because now if a combination is in both manual and old planning, then the exception is thrown, but this is not neccesarry, it is only neccesaary to change the value to one. instead of the sum of the two plannings.
                    requirement_failed = True
                    failed_combinations.append([empl_line, time])
            
            if requirement_failed == True:
                print(f'"Hours planned per empl_line at given moment" restriciton is not met in {name_planning}')
                print(f'The following combinations where the cause of the failed requirements: \n {failed_combinations}')
                raise ValueError(f'"Hours planned per empl_line at given moment" restriction is not met in {name_planning}, the following combinations where the cause: {failed_combinations}')

        def checkRequiredHoursPlannedUpperboundForPlanning(self, planning_df: pd.DataFrame, name_planning: str):
            # Possibly also add the old planning? because that is taken as an absolute aswell. 
            requiredHoursPlanned_help = planning_df.copy().reset_index()
            
            group_cols = feasability_dfs.get('order_suborder_vs_allocation')[1]
            sum_col = feasability_dfs.get('order_suborder_vs_allocation')[2]
            requiredHoursPlanned: pd.DataFrame = requiredHoursPlanned_help.groupby(group_cols)[sum_col].sum()
            
            requirement_failed = False
            failed_combinations = []

            for idx in requiredHoursPlanned.index:
                order_suborder = idx
                upperbound = self.required_hours_df.loc[order_suborder].iloc[1]

                if (requiredHoursPlanned.loc[order_suborder] > upperbound).any():
                    requirement_failed = True
                    excess_hours = (requiredHoursPlanned.loc[order_suborder] - upperbound).values.item()
                    
                    failed_combinations.append([order_suborder, f'X excess hours planned, with X={excess_hours}'])
            
            if requirement_failed == True:
                print(f'"Hours planned for order_suborder less than or equal to upperbound" restriciton is not met in {name_planning}')
                print(f'The following combinations where the cause of the failed requirements: \n {failed_combinations}')
                raise ValueError(f'"Hours planned for order_suborder less than or equal to upperbound" restriction is not met in {name_planning}, the following combinations where the cause: {failed_combinations}')
        #FIXME: Add a checker for specifics from the orders_df, such as specific line etc. 

        def checkSpecificLinesForPlanning(self, planning_df: pd.DataFrame, name_planning: str):
            specificLinePlanned_help = planning_df.copy().reset_index()
            
            group_cols = feasability_dfs.get('order_suborder_vs_empl_line')[1]
            sum_col = feasability_dfs.get('order_suborder_vs_empl_line')[2]
            specificLinePlanned: pd.DataFrame = specificLinePlanned_help.groupby(group_cols)[sum_col].sum()

            specific_line_df = self.specific_production_line
            
            requirement_failed = False
            failed_combinations = []

            for idx in specificLinePlanned.index:
                order_suborder = idx[0]
                empl_line = idx[1]

                if order_suborder in specific_line_df.index:
                    specific_line = specific_line_df.loc[order_suborder].iloc[0]
                    if specific_line != '':
                        if specificLinePlanned.loc[order_suborder, empl_line].iloc[0] ==1:
                            if empl_line != specific_line:
                                requirement_failed = True

                                failed_combinations.append([order_suborder, empl_line])
            
            if requirement_failed == True:
                print(f'"Specific line restriction" was not met in {name_planning}')
                print(f'The following combinations where the cause of the failed requirements: \n {failed_combinations}')
                raise ValueError(f'"Specific line restriction" was not met in {name_planning}, The following combinations where the cause of the failed requirements: \n {failed_combinations}' )








                