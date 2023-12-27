from problem_declaration.models import EWOptimisation

from general_configuration import feasability_dfs

import pandas as pd
import sys

class SolvabilityTest:
    """This class contains several subclasses which perform checks on the data before solving, such that possible infeasibilities may already be found.
    """
    def __init__(self):
        pass
    
    class TestProblemFormulation(EWOptimisation):
        pass
    
    #TODO: ALSO ADD VBA CHECKING FOR THE MANUAL_PLANNING SHEET. 
    class TestPlanningEW():
        """This subclass of SolvabilityTest checkt the solvability of 'Planning of EW'

        Raises:
            ValueError: _description_
            ValueError: _description_
            ValueError: _description_
            ValueError: _description_
            ValueError: _description_
            ValueError: _description_
            ValueError: _description_
        """
        #FIXME: The check in 'Input PYTHON' in 'Handmatig Plannen' where 'Incompleet' is checked, could be added. But only after the reorginisation of 'data' because then you can add a instance variable that keeps a list of index combinations that have NaN values. 
        # Also, check whether initialising with a dataframesclass, eventough there already was a super initialised results in errors.
        def __init__(self, ewOptimisation: EWOptimisation):
            """Constructor of the TestPlanningEW object

            Args:
                ewOptimisation (EWOptimisation): pyomo model for the EW Optimisation.
            """
            self.failed_checks = []

            self.dataframes_class = ewOptimisation.dataframes_class

            self.list_order_suborder = ewOptimisation.list_order_suborder
            self.list_time = ewOptimisation.list_time
            self.list_employee_line = ewOptimisation.list_employee_line
            self.list_employee = ewOptimisation.list_employee
            self.list_line = ewOptimisation.list_line

            self.manual_planning_df = ewOptimisation.manual_planning_df
            self.old_planning_df = ewOptimisation.old_planning_df
            self.availability_df = ewOptimisation.availability_df
            self.skills_df = ewOptimisation.skills_df

            self.orders_df = self.dataframes_class.get_dataframe_by_name('orders_df').get_pandas_dataframe().copy()
            self.specific_order_suborder_df = self.dataframes_class.get_dataframe_by_name('order_specific_df').get_pandas_dataframe().copy()
            self.required_hours_df = self.dataframes_class.get_dataframe_by_name('time_req_df').get_pandas_dataframe().copy()
            self.specific_production_line = self.dataframes_class.get_dataframe_by_name('specific_line_df').get_pandas_dataframe().copy()

        
        # HELPER FUNCTION
        def group_df(self, dataframeToGroup : pd.DataFrame, groupingName: str) -> pd.DataFrame:
            """This function groups the inputted dataframe, based on the index- and sumcolumns saved in the feasability_dfs dictionary. 

            Args:
                dataframeToGroup (pd.DataFrame): Dataframe to group
                groupingName (str): name of grouping in the feasability_dfs dictionary

            Returns:
                pd.DataFrame: The grouped dataframe.
            """
            #FIXME: Possibly create a dataframe in dataframes for this. or do this in the cleaning? except if in other checks the sum is not needed, but the normal version.
            group_cols = feasability_dfs.get(groupingName)[1] # Columns to group the dataframe by
            sum_col = feasability_dfs.get(groupingName)[2] # Columns to sum the grouped dataframe by
            groupedDataframe = dataframeToGroup.groupby(group_cols)[sum_col].sum()

            return groupedDataframe

        #TODO:
        # Also, for which planning do the checks neet to happen, once for combined planning or for each individual planning? probably each individual planning, since the end user needs to be able to lookup where it went wrong.
        # make a helpfunction for the 'group' part. 
        def checkAll(self):
            """
            This method performs all the necessary checks, and reports back whether there are any. 
            It performs the checks for three types of plannings:
                Old_planning, Manual_planning, Combined_Planning. 
            Note that if the either of the first two fail a test, then Combined_Planning will also fail the test, since combined_planning is a concateantion of the previous.

            The tests performed are:
                Availability test: Tests whether during the allocations the empl_line are available, given the availability input in excel.
                Skill test: Tests whether given allocations the empl_line are permitted to perform a certain suborder, given skills in excel.
                Required hours: Tests whether given allocations do not exceed the upperbound of their required time to finish
                Specific lines: Tests whether allocations do not allocate an order_suborder to an empl_line that is not specified as the sole option for that order_suborder.
                Timeline availability: Tests whether the total required time does not exceed the available time in the given timeline.
            """
            checks = [self.checkManualPlanning, self.checkOldPlanning, self.checkOldJOINEDManualPlanning]

            self.failed_checks.clear()

            for check in checks:
                try:
                    check()
                except Exception as e: 
                    self.failed_checks.append(ic(e))

            if self.failed_checks:
                number_of_failed_checks = len(self.failed_checks)
                print(f"There are {number_of_failed_checks} checks that failed. They represent the following problems: (Please resolve these issues inorder to proceed.)")
                for check_error in self.failed_checks:
                    print(check_error)
                    print()
                sys.exit()
            else:
                print("All checks passed!")

        def checkManualPlanning(self):
            """This function checks the tests for the manual planning.
            """
            planning = self.manual_planning_df
            name_planning = 'Manual Planning'

            self.check_planning_restrictions(planning_df=planning, name_planning=name_planning)
                
        def checkOldPlanning(self):
            """This function checks the tests for the old planning.
            """
            planning = self.old_planning_df
            name_planning = 'Old Planning'

            self.check_planning_restrictions(planning_df=planning, name_planning=name_planning)

        def checkOldJOINEDManualPlanning(self):
            """This function checks the tests for the combined planning, that is both the .
            """
            if not self.old_planning_df.empty and not self.manual_planning_df.empty:
                planning = pd.concat([self.old_planning_df, self.manual_planning_df]).drop_duplicates(keep='first')
            elif not self.old_planning_df.empty and self.manual_planning_df.empty:
                planning = self.old_planning_df
            elif self.old_planning_df.empty and not self.manual_planning_df.empty:
                planning = self.manual_planning_df
            else:
                planning = pd.DataFrame
            
            name_planning = 'Old AND/OR Manual planning'

            self.check_planning_restrictions(planning_df=planning, name_planning=name_planning) 
        
        def check_planning_restrictions(self, planning_df: pd.DataFrame, name_planning: str):
            """This function checks all restrictions for a given planning. The name of the planning is used when presenting the errors. 
            
            The tests performed are:
                Availability test: Tests whether during the allocations the empl_line are available, given the availability input in excel.
                Skill test: Tests whether given allocations the empl_line are permitted to perform a certain suborder, given skills in excel.
                Required hours: Tests whether given allocations do not exceed the upperbound of their required time to finish
                Specific lines: Tests whether allocations do not allocate an order_suborder to an empl_line that is not specified as the sole option for that order_suborder.
                Timeline availability: Tests whether the total required time does not exceed the available time in the given timeline.

            Args:
                planning_df (pd.DataFrame): planning df from excel to check
                name_planning (str): name of the planning (shown when an error happens to indicate where the problem lies)
            """
            if not planning_df.empty:
                self.checkAvailabilityForPlanning(planning_df=planning_df, name_planning=name_planning)
                self.checkSkillForPlanning(planning_df=planning_df, name_planning=name_planning)
                self.checkRequiredHoursPlannedUpperboundForPlanning(planning_df=planning_df, name_planning=name_planning)
                self.checkSpecificLinesForPlanning(planning_df=planning_df, name_planning=name_planning)
                self.checkAvailabilityOfNumberOfHoursNeeded(planning_df=planning_df, name_planning=name_planning)
        
        def checkAvailabilityForPlanning(self, planning_df: pd.DataFrame, name_planning: str):
            """This check makes sure that the planning follows the availability constraint. That is, for all employee_line's their maximum availability is not exceeded at any given time. 

            Args:
                planning_df (pd.DataFrame): planning df from excel to check
                name_planning (str): name of the planning (shown when an error happens to indicate where the problem lies)

            Raises:
                ValueError: Indicates that an 'availability' error is present in the "name_planning", and reports for which records the errors are present.
            """
            empl_lineTime_help = planning_df.copy().reset_index()
            
            # Obtain the sum of allocations for each employee_line for each time.
            empl_lineTime = self.group_df(empl_lineTime_help, 'empl_line_vs_Time')
    
            requirement_failed = False
            failed_combinations = []

            # loop through each employee_time and time and check whether any of these values has an allocation (value >=1), if so check whether this exceeds their availability.
            for idx in empl_lineTime.index:
                empl_line = idx[0]
                time = idx[1]
                if (empl_lineTime.loc[empl_line, time] >= 1).any(): # note the values are integers, since allocation is a binary.
                    if not empl_lineTime.loc[empl_line, time].iloc[0] >= self.availability_df.loc[time, empl_line]: # Check whether the total allocations per empl_line per time exceeds their availability.
                        requirement_failed = True 
                        failed_combinations.append([empl_line, time]) # Add all (employee_line, time) combinations that exceed the availability.
            
            if requirement_failed == True: # If there is an error in the inputted planning, return a error that indicates where these error lie. 
                raise ValueError(f'"Empl_line should be available when planned" restriction not met in {name_planning}. \n The following combinations were the cause: \n\n {failed_combinations}. \n\n This means that for the above combinations, the planned employee or line is not available at the given time.')

        def checkSkillForPlanning(self, planning_df: pd.DataFrame, name_planning: str):
            """This check makes sure that there are no allocations where the employee_line is not skilled to perform the specific suborder.

            Args:
                planning_df (pd.DataFrame): planning df from excel to check
                name_planning (str): name of the planning (shown when an error happens to indicate where the problem lies)

            Raises:
                ValueError: Indicates that a 'skill' error is present in the "name_planning", and reports for which records the errors are present.
            """
            order_suborderEmpl_line_help = planning_df.copy().reset_index()
            
            # Obtain the sum of allocations for each employeeline for each time.
            order_suborderEmpl_line = self.group_df(order_suborderEmpl_line_help, 'order_suborder_vs_empl_line')

            # For extracting the suborder for a unique order_suborder combination.
            specific_order = self.specific_order_suborder_df

            requirement_failed = False
            failed_combinations = []

            # Loop through each employee and order_suborder to check whether any of these values violate the skill constraint.
            for idx in order_suborderEmpl_line.index:
                order_suborder = idx[0]
                empl_line = idx[1]
                suborder = specific_order.loc[order_suborder].iloc[1]

                # Check whether the empl_line is skilled to perform a specific suborder.
                if self.skills_df.loc[empl_line, suborder] == 0 and (order_suborderEmpl_line.loc[order_suborder, empl_line].iloc[0] >= 1).any():
                    requirement_failed = True
                    failed_combinations.append([order_suborder, empl_line]) # add the (order_suborder, employee_line) combinations that result in the errors.
            
            if requirement_failed == True: # If there is an error in the inputted planning, return a error that indicates where these error lie. 
                raise ValueError(f'"Empl_line should possess skills for planned suborder" restriction not met in {name_planning}. \n The following combinations were the cause: \n\n {failed_combinations}. \n\n This means that an employee is planned more than ones at a given moment. This could be due to being planned twice, once in manual_planning and once in the old_planning.')
            
            if requirement_failed == True:
                raise ValueError(f'"Hours planned per empl_line at given moment" restriction is not met in {name_planning}. \n The following combinations were the cause: \n\n {failed_combinations}. \n\n ')

        #FIXME: What if it is necessary to exceed it because of underestimation, how can one sucombe that?
        def checkRequiredHoursPlannedUpperboundForPlanning(self, planning_df: pd.DataFrame, name_planning: str):
            """This check makes sure that the planning does not exceed the needed amount of hours upperbound. 

            Args:
                planning_df (pd.DataFrame): planning df from excel to check
                name_planning (str): name of the planning (shown when an error happens to indicate where the problem lies)

            Raises:
                ValueError: Indicates that a 'required hours planned' error is present in the "name_planning", and reports for which records the errors are present.
            """
            # Possibly also add the old planning? because that is taken as an absolute aswell. 
            hoursPlanned_help = planning_df.copy().reset_index()
            
            # Obtain the sum of allocations for each employee_line for each time.
            hoursPlanned = self.group_df(hoursPlanned_help, 'order_suborder_vs_allocation')
            
            requirement_failed = False
            failed_combinations = []

            # Loop through the different order_suborders and check the scheduled amount of hours vs the required.
            for idx in hoursPlanned.index:
                order_suborder = idx
                upperbound = self.required_hours_df.loc[order_suborder].iloc[1]
                hoursScheduled = hoursPlanned.loc[order_suborder]

                if (hoursScheduled > upperbound).any(): # if the scheduled amount of hours is larger than the required amount, an error has occured.
                    requirement_failed = True
                    excess_hours = (hoursScheduled - upperbound).values.item()
                    
                    failed_combinations.append([order_suborder, f'X excess hours planned, with X={excess_hours}. There is a maximum of {upperbound} that can be scheduled.'])
            
            if requirement_failed == True:
                raise ValueError(f'"Hours planned for order_suborder less than or equal to upperbound" restriction is not met in {name_planning}. \n The following combinations were the cause: \n\n {failed_combinations}\n\n This means these orders are scheduled too many times, such that they have exceeded their required amount of hours.')

        def checkSpecificLinesForPlanning(self, planning_df: pd.DataFrame, name_planning: str):
            """This check makes sure that if an order_suborder must be performed on a specific line, that it will not be allocated to another. 

            Args:
                planning_df (pd.DataFrame): planning df from excel to check
                name_planning (str): name of the planning (shown when an error happens to indicate where the problem lies)

            Raises:
                ValueError: Indicates that a 'specific line' error is present in the "name_planning", and reports for which records the errors are present.
            """
            specificLinePlanned_help = planning_df.copy().reset_index()
            
            # Obtain the sum of order_suborders planned for specific employee_lines
            specificLinePlanned = self.group_df(specificLinePlanned_help, 'order_suborder_vs_empl_line')
            group_cols = feasability_dfs.get('order_suborder_vs_empl_line')[1]
            sum_col = feasability_dfs.get('order_suborder_vs_empl_line')[2]
            specificLinePlanned: pd.DataFrame = specificLinePlanned_help.groupby(group_cols)[sum_col].sum()

            specific_line_df = self.specific_production_line
            
            requirement_failed = False
            failed_combinations = []

            # Loop through the (order_suborder, employee_line) combinations.
            for idx in specificLinePlanned.index:
                order_suborder = idx[0]
                empl_line = idx[1]

                if order_suborder in specific_line_df.index: # Check whether the order_suborder exists in the specific_line dataframe. That is, the order has a specific line on which it must be performed. 
                    # if it does, obtain the specific line on which the order might need to be allocated.
                    specific_line = specific_line_df.loc[order_suborder].iloc[0]
                    if specific_line != '': 
                        if specificLinePlanned.loc[order_suborder, empl_line].iloc[0] == 1: 
                            if empl_line != specific_line: # If the empl_line is not equal to the required specific line
                                requirement_failed = True

                                failed_combinations.append([order_suborder, empl_line])
            
            if requirement_failed == True:
                raise ValueError(f'"Specific line restriction" was not met in {name_planning}, The following combinations were the cause of the failed requirements: \n\n {failed_combinations}' )
            
        #FIXME: Add a checker for specifics from the orders_df, such as specific line, number of hours needed etc. 
        # Testing restrictions for the model, which are not about the planning.
        def checkAvailabilityOfNumberOfHoursNeeded(self, planning_df: pd.DataFrame, name_planning: str): #FIXME: Add a way to get all the combinations that are possible, without 'counting' certain points double. That is, if someone does MAG, they cannot also preform SMD at that same moment => lower maximum per suborder. 

            # create a df that gets the maximum amount of allocations per suborder
            max_numberOfAllocationsPerSuborder_df = self.availability_df.dot(self.skills_df).sum(axis=0)

            # the maximum of total allocations is:
            max_numberOfAllocations = self.availability_df.sum(axis=0).sum(axis=0)

            # find a way to make a list of not just the max per suborder, but for all possible combinations where employees are allocated once per time interval 
            allowedCombinationsList = []

            # Needed number of allocations per suborder
            group_cols = feasability_dfs.get('specific_order_req_time_df')[1]
            sum_col = feasability_dfs.get('specific_order_req_time_df')[2]
            reqTimePerSuborder = self.orders_df.copy().reset_index().groupby(group_cols)[sum_col].sum()

            # how to cleaverly check whether a combination is possible, add one to each suborder each time or? is there a way to use like ai. 

            
            # checks whether there is asked to schedule more than is even possible in the given time ranges.
            print(reqTimePerSuborder)
            if reqTimePerSuborder.sum(axis=0).iloc[0] > max_numberOfAllocations:
                raise ValueError(f'"Hour availability in Planning" was not met in {name_planning}, The total sum of all required time intervals were the cause of the failed requirements')

            allowed = True
            # for combination in allowedCombinationsList:
            for suborder in max_numberOfAllocationsPerSuborder_df.index:
                if suborder != 'NONE':
                    # checks whether more time is required for a suborder than is possible in the given time ranges
                    if max_numberOfAllocationsPerSuborder_df.loc[suborder] < reqTimePerSuborder.loc[suborder].iloc[0]:
                        allowed = False
                        raise ValueError(f'"Hour availability in Planning" was not met in {name_planning}, The sum of all required time intervals were the cause of the failed requirements in the following suborder: {suborder}')

            """for suborder in max_numberOfAllocationsPerSuborder_df.index:
                # checks whether more time is required than there is in the current combination.
                if combination.loc[suborder] < reqTimePerSuborder.loc[suborder]:
                    allowed = False
                    break # Break or Raise? same as above"""
            
            # checks whether the current combination completed all tests, if so the program can be stopped because there should not be any problems with the hours needed for the planning, as there is at least one 'solution' for the allocation of time over suborders.
            if allowed == True:
                pass # a possible solution format has been found, so no need to search further. 
                    
            # is there a way to make a list of all possible combinations, that are valid. That is a a person can only be allocated once every time interval. 

        #Also add the check above, but then for people, such that needed planned hours per persion(that is specific_line) is enough. 

