import pyomo
import pyomo.opt
import pyomo.environ as pyo
import pandas as pd
import logging
from icecream import ic
import sys

from data.dataframe import Dataframe
from data.dataframes import Dataframes
from data.data_index import Data_Index

from general_configuration import dfs, old_planning_limit



from data.data import (
    ManagerDataframes, 
    IndexSetsDataframe,
    OrderDataframe
    )

""" 
Aks in ChatGPT:
how to keep your complicated pyomo project organised, that is if i use variables and sets then i define them as: self.m.var/set because of this i cannot autocomplete or get recommendations for arguments inside the var/set. If i work in a large project this results in difficulties keeping track of the correct indexes and var/set names. How can i overcome this difficulty?

What if we make it a shortest path problem. minimizing the maximum length of each order with a non specified starting point.
That is you apply the A* algorithm to the optimisation. with length of the needed time to complete. https://www.youtube.com/watch?v=A60q6dcoCjw
This way you first minimize the actual schedule before assigning the specific jobs to people. It still remains to find a way to have correct lengths for the jobs without being able to differentiate a hour having one worker or multiple work on the project and thus reducing the length. 
"""

class EWOptimisation:
    """
    This class implements the pyomo optimisation problem for EW. It contains functions to create the model, then all the constraints are automatically added aswell. It also allows solving and exporting the solutions to excel.
    """
    def __init__(self, managerDF: ManagerDataframes):
        """Constructor of the EWOptimisation model. Takes in a 'Dataframes' object

        Args:
            dataframes_class (Dataframes): Dataframes to use inside the model. 
        """
        self.managerDF = managerDF 

        # Obtain specific DF's
        self.orderDF = self.managerDF.get_Dataframe('OrderDF', expected_return_type_input=OrderDataframe)
        self.indexDF = self.managerDF.get_Dataframe('IndexDF', expected_return_type_input=IndexSetsDataframe)
        
        
        # Get from solutionDF
        self.excel_file = self.managerDF.get_Dataframe('SolutionDF').pandas_ExcelFile  # All dataframes come from the same file. That is why it simply selects the first dataframe and gets the excelfile. 

        self.model_created : bool = False

        self.solution = pd.DataFrame()
        self.short_solution = pd.DataFrame()

        self.initialized_EWOptimisation = True
        
    def createModel(self):
        """Creates the pyomo model that optimizes the production planning for EW. \n

        THE OBJECTIVE FUNCTION:
            MINIMIZE: ALLOCATION * PENALTY + 400 * VAR_GAPS + 400 * VAR_BEFORE
            
            THAT IS:
                THE PENALTY FOR ALLOCATING A CERTAIN ORDER AT A SPECIFIC TIME \n
                + 400 * EACH GAP INSIDE INDIVIDUAL ORDER SCHEDULES \n
                + 40 * EACH TIME THAT AN ORDER HAS NOT STARTED YET
        \n\n
        THE CONSTRAINTS:
                RULES THAT IMPLEMENT ORDER_SUBORDER SPECIFICS \n
            REQUIRED HOURS MUST BE SCHEDULED FOR AN ORDER_SUBORDER \n

                RULES THAT IMPLEMENT EMPLOYEE_LINE SPECIFICS \n
            EMPLOYEE_LINE ONLY ALLOCATED ONCE PER TIME \n
            EMPLOYEE_LINE ONLY ALLOWED TO PERFORM SUBORDER IF SKILLED. \n
            EMPLOYEE_LINE ONLY ALLOWED ALLOCATED IF AVAILABLE. \n\n

                RULES THAT IMPLEMENT THAT NEXT SUBORDERS CANNOT BE STARTED BEFORE PREVIOUS SUBORDER IS COMPLETED (FOR ATLEAST X%) \n
            PREVIOUS SUBORDER MUST BE COMPLETED FOR ATLEAST X% \n
            PREVIOUS SUBORDER MUST BE COMPLETED FOR A LARGER PERCENTAGE THAN THE NEXT SUBORDER \n\n

                RULES THAT IMPLEMENT THAT ORDERS ARE ALLOCATED ONLY TO SPECIFIC (TYPE OF) LINES OF EMPLOYEES. \n
            LINE ORDERS ALLOCATED TO LINES \n
            SPECIFIC LINE ORDERS ALLOCATED TO THE SPECIFIC LINE \n
            MANUAL ORDERS ALLOCATED TO EMPLOYEES \n\n

                RULES THAT IMPLEMENT THE OLD- AND MANUAL PLANNING. \n
            OLD PLANNING // currently inactive, but indirectly active via 'COMBINED PLANNING' \n
            MANUAL PLANNING // currently inactive, but indirectly active via 'COMBINED PLANNING' \n
            COMBINED PLANNING \n\n

                RULES THAT IMPLEMENT THE GAPS IDENTIFICATION. \n
            BEFORE INDICATES IF THE ORDER_SUBORDER HAS BEEN ALLOCATED BEFORE SPECIFIC TIME \n
            AFTER INDICATES IF THE ORDER_SUBORDER HAS BEEN ALLOCATED AFTER A SPECIFIC TIME \n
            DURING INDICATES IF AT A CERTAIN TIME THE ORDER HAS BEEN STARTED AND HAS NOT YET BEEN FINISHED, THUS INDICATES ALL TIME INTERVALS BETWEEN START AND FINISH OF ORDER \n
            GAPS INDICATES IF BETWEEN THE START AND FINISH TIMES OF AN ORDER_SUBORDER, THE IS AN NOT ALLOCATION AT A CERTAIN TIME. THAT IS, THERE IS A GAP IN THE SCHEDULE. 

        """
        self.m = pyo.ConcreteModel()

        ### Retrieving data
        # Retrieve sets/lists
        self.list_order_suborder = self.indexDF.order_suborder
        self.list_suborder_set = self.indexDF.suborders
        self.list_time = self.indexDF.time_intervals
        self.list_employee_line = self.indexDF.employee_line
        self.list_employee = self.indexDF.employee
        self.list_line = self.indexDF.line

        # Retrieve dataframes that represent specific columns of the 'order_df'. 
        self.dates_df = self.orderDF.dates_df
        self.revenue_df = self.orderDF.revenue_df
        self.time_req_df = self.orderDF.time_req_df
        self.specific_order_suborder = self.orderDF.specific_order_df
        self.specific_line_df = self.orderDF.specific_line_df
        self.exec_on_line_df = self.orderDF.executed_on_line_df

        # Obtain series of the above mentioned df's for easy usage throughout this file.
        self.date_start = self.dates_df.iloc[:, 0]
        self.date_deadline = self.dates_df.iloc[:, 1]
        self.revenue = self.revenue_df.iloc[:, 0]
        time_req_lb = self.time_req_df.iloc[:, 0]
        time_req_ub = self.time_req_df.iloc[:, 1]

        # Retrieve the dataframes containing the (manipulated) data from excel.
        self.skills_df = self.managerDF.get_Dataframe('SkillsDF').pandas_Dataframe
        self.availability_df = self.managerDF.get_Dataframe('AvailabilityDF').pandas_Dataframe
        
        self.penalty_df = self.managerDF.get_Dataframe('PenaltyDF').pandas_Dataframe
        
        self.suborders_df = self.orderDF.next_prev_suborder_df
        self.percentage_df = self.orderDF.percentage_df
        
        self.old_planning_df = self.managerDF.get_Dataframe('OldPlanningDF').pandas_Dataframe
        self.manual_planning_df = self.managerDF.get_Dataframe('ManualPlanningDF').pandas_Dataframe
        self.combined_planning_df = self.managerDF.get_Dataframe('CombinedPlanningDF').pandas_Dataframe

        # Create dataframe where unique_code can be looked for by using specific order and suborder. (order, suborder) -> (order_suborder)
            # NOTE: This can be made a 'specific' function if we implement subclasses of the dataframe class, like it is stated in the todo's
            # RENAME: reverseSearch_specific_order_suborder?!
        transpose_specific_order_suborder = self.specific_order_suborder.copy()
        transpose_index = self.specific_order_suborder.columns.to_list()
        transpose_specific_order_suborder.reset_index(inplace=True)
        transpose_specific_order_suborder.set_index(transpose_index, inplace=True)

        ### Create needed sets, variables and parameters for the model.
        # Create sets for the model
        self.m.set_order_suborder = pyo.Set(initialize=self.list_order_suborder, name='set_order_suborder', doc='Set of all combinations of orders and suborders')
        self.m.set_time = pyo.Set(initialize=self.list_time, name='set_time', doc='Set of all time intervals')
        self.m.set_employee_line = pyo.Set(initialize=self.list_employee_line, name='set_employee_line', doc='Set of all production lines and employees')
        self.m.set_employee = pyo.Set(initialize=self.list_employee, name='set_employee', doc='Set of all employees')
        self.m.set_line = pyo.Set(initialize=self.list_line, name='set_line', doc='Set of all production lines')
        
        self.m.set_alloc_index = pyo.Set(initialize=self.m.set_order_suborder * self.m.set_time * self.m.set_employee_line)
        self.m.set_gaps_index = pyo.Set(initialize=self.m.set_order_suborder * self.m.set_time)

        # Create the upperbounds for constraints in the model.
        self.upperbound = len(self.m.set_order_suborder) * len(self.m.set_time) * len(self.m.set_employee_line)
        self.m.upperbound_of_employee = len(self.m.set_employee_line)
        self.m.upperbound_of_time = len(self.m.set_time)
        self.m.upperbound_of_employees_and_time = len(self.m.set_employee_line) * len(self.m.set_time)
    
        # Create variables for the model
        self.m.var_alloc = pyo.Var(self.m.set_alloc_index, domain=pyo.Binary, name='var_alloc', doc="Represents the allocation of order_suborder's at a specific time, performed by an employee_line") 

        self.m.var_indicator_alloc_sum_employee_line = pyo.Var(self.m.set_gaps_index, domain=pyo.Binary, name='var_indicator_alloc_sum_employee_line', doc='Represents an allocator that has value 1 when at least one employee_line has been scheduled else value 0')
        
        # In the next 'doc's, 'Including' means: if var_alloc(51124_MAG, 09:00:00) = 1 and then the entire production is finished, 
        # then var_after(51124_MAG, 08:00:00) = var_after(51124_MAG, 09:00:00) = 1, but var_after(51124_MAG, 10:00:00)=0
        # then var_before(51124_MAG, 08:00:00) = 0 , but var_before(51124_MAG, 09:00:00) = var_before(51124_MAG, 10:00:00) = ... = 1
        self.m.var_before = pyo.Var(self.m.set_gaps_index, domain=pyo.Binary, name='var_gaps_before', doc="Represents the sum of allocations before (and including) a specific combination of (order_suborder, time)")
        self.m.var_after = pyo.Var(self.m.set_gaps_index, domain=pyo.Binary, name='var_gaps_after', doc="Represents the sum of allocations after (and including) a specific combination of (order_suborder, time)") 
        self.m.var_during = pyo.Var(self.m.set_gaps_index, domain=pyo.Binary, name='var_gaps_during', doc="Represents the entire period that an order_suborder is scheduled, from start till finish. (var_alloc only gives allocated combination value 1, this also gives combination inbetween start and finish that represent a 'gap' value 1)")
        self.m.var_gaps = pyo.Var(self.m.set_gaps_index, domain=pyo.Binary, name='var_gaps', doc="Represents all the gaps that an order_suborder allocation has.")

        #FIXME: MAKE A CORRECT OBJECTIVE FUNCTION THAT PRIORITIZES THE MOST IMPORTANT ORDERS.
        # Create objective function
        def rule_objectiveFunction(m):
            """This rule minimizes the penalty that allocation get, but also the gaps inside an allocation, that is minimize the amount of gaps between the starting and ending time interval of the order_suborder and \n minimizes the gaps before an allocation, so between the startdate of the timeline and the first allocation of the order_suborder.

            Minimizes: 
            [allocation * penalty_df](per order_suborder, time, employee_line) # penalty to schedule a certain order at a specific time.
            +
            400 * [gaps](order_suborder, time) # penalty for the entire allocation between the start and end date. 
            +
            40 * [1- before](order_suborder, time) # penalty for leaving a gap between the startdate of the timeline and the first allocation of the order_suborder.

            Args:
                m (pyo.ConcreteModel()): pyomo model

            Returns:
                float: The total penalty, does not represent a 'true' value. 
            """
            penalty = \
                sum(
                    m.var_alloc[i, j, k] * self.penalty_df.loc[j, i]
                    for i in m.set_order_suborder
                    for j in m.set_time
                    for k in m.set_employee_line
                ) + \
                sum(
                    m.var_gaps[(i, j)] * 400
                    for i in m.set_order_suborder
                    for j in m.set_time
                ) + \
                sum(
                    (1 - m.var_before[(i, j)]) * 40
                    for i in m.set_order_suborder
                    for j in m.set_time
                )
            
            return penalty
        self.m.objectiveFunction = pyo.Objective(rule=rule_objectiveFunction(self.m), sense=pyo.minimize)

        ### Create Constraints

        ### RULES THAT IMPLEMENT ORDER_SUBORDER SPECIFICS
        # REQUIRED HOURS MUST BE SCHEDULED FOR AN ORDER_SUBORDER
        def rule_requiredPlannedHours(m, i):
            """This rule makes sure all order_suborder {i} meet their required amount of planned hours, that is it's lower and upperbound. 
            
            Note: The sum in the restriction gives the total amount of planned hours per order.

            Args:
                m (pyo.ConcreteModel()): Model
                i (str): order_suborder index

            Returns:
                Expression: time_req_lb <= allocation(sum over time and employee_line) <= req_time_up
            """
            return (
                time_req_lb.loc[i],
                sum(
                    m.var_alloc[(i, j, k)] 
                    for j in m.set_time 
                    for k in m.set_employee_line
                ),
                time_req_ub.loc[i]
            )
        self.m.constr_required_planned_hours = pyo.Constraint(self.m.set_order_suborder, rule=rule_requiredPlannedHours)

        ### RULES THAT IMPLEMENT EMPLOYEE_LINE SPECIFICS
        # EMPLOYEE_LINE ONLY ALLOCATED ONCE PER TIME 
        def rule_oneAllocPerEmpl_linePerMoment(m, j, k):
            """This rule makes sure that at any given time {j} every employee and/or line {k} is allocated a maximum of one time.

            Args:
                m (pyo.ConcreteModel()): pyomo model
                j (datetime): time index
                k (str): employees_lines index

            Returns:
                Expression: 0 <= allocation(sum over order_suborder) <= 1
            """
            return (
                0, 
                sum(m.var_alloc[(i, j, k)]
                    for i in m.set_order_suborder
                ),
                1
            )
        self.m.constr_oneAllocPerEmpl_linPerMoment = pyo.Constraint(self.m.set_time, self.m.set_employee_line, rule=rule_oneAllocPerEmpl_linePerMoment)

        # EMPLOYEE_LINE ONLY ALLOWED TO PERFORM SUBORDER IF SKILLED.
        def rule_onlyAllocIfEmpl_lineSkilled(m, i, k):
            """This rule makes sure that an employee and/or line {k} can only be allocated to a suborder {i} if it is skilled to do so.

            Args:
                m (pyo.ConcreteModel()): pyomo Model
                i (str): order_suborder index
                j (datetime): time index
                k (str): employees_lines index

            Returns:
                Expression: 0 <= allocation(sum over time) <= 1 (skills_df has binary value (0/1))
            """
            suborder = self.specific_order_suborder.loc[i].iloc[1]
            return (0, 
                    sum(
                        m.var_alloc[(i, j, k)] 
                        for j in m.set_time
                        ), 
                    m.upperbound_of_time * self.skills_df.loc[k, suborder]
                    ) # NOTE: Instead of creating a constraint for each individual 'time' index, we sum over the entire 'time' index to reduce the amount of constraints, leading to quicker solving times. 
        self.m.constr_onlyAllocIfEmpl_lineSkilled = pyo.Constraint(self.m.set_order_suborder, self.m.set_employee_line, rule= rule_onlyAllocIfEmpl_lineSkilled)

        # EMPLOYEE_LINE ONLY ALLOWED ALLOCATED IF AVAILABLE.
        def rule_onlyAllocIfEmpl_lineAvailable(m, i, j, k):
            """This rule makes sure that an employee and/or line {k} can only be allocated at a time {j} on an order_suborder {i} if they are available to do so.

            Args:
                m (pyo.ConcreteModel()): pyomo Model
                i (str): order_suborder index
                j (datetime): time index
                k (str): employees_lines index

            Returns:
                Expression: 0 <= allocation <= 1 (availability_df has value of either 0 or 1)
            """
            return (0, 
                    m.var_alloc[(i, j, k)], 
                    self.availability_df.loc[j, k])  
        self.m.constr_onlyAllocIfEmpl_lineAvailable = pyo.Constraint(self.m.set_order_suborder, self.m.set_time, self.m.set_employee_line, rule= rule_onlyAllocIfEmpl_lineAvailable)

        ### RULES THAT IMPLEMENT THAT NEXT SUBORDERS CANNOT BE STARTED BEFORE PREVIOUS SUBORDER IS COMPLETED (FOR ATLEAST X%)

        # HELPER FUNCTION
        def get_previous_suborder(i):
            """Gets the previous order_suborder for a given order_suborder {i}. If there is no previous suborder 'None' is returned, if there is a previous suborder a list with attributes of the previous suborder is returned. 

            Args:
                i (str): order_suborder index

            Returns:
                List: if there is a previous suborder: [order, suborder, percentage, prev_suborder_index, prev_order_suborder], if there is no previous suborder: None. /n So, in handling the case where there is no previous suborder one can check if the output is 'None'
            """
            order = self.specific_order_suborder.loc[i].iloc[0]
            suborder = self.specific_order_suborder.loc[i].iloc[1]
            percentage = self.percentage_df.loc[i].iloc[0]

            # Not all orders follow the same route through the suborders. To prevent this from resulting in problem, we loop through each previous suborder until we find the first present suborder.
            # NOTE:This might be improved by adding a prev_sub and next_sub to the orders_df, but this is dependent on which data the client stores for connections between orders.
            prev_suborder_index = self.list_suborder_set.index(suborder) - 1
            prev_order_suborder = None
            while prev_suborder_index > 0:
                prev_suborder = self.list_suborder_set[prev_suborder_index]
                try:
                    prev_order_suborder = transpose_specific_order_suborder.loc[order, prev_suborder].iloc[0]
                    break # valid previous suborder found
                except KeyError:
                    prev_order_suborder = None
                    prev_suborder_index -= 1
                    continue
            
            if prev_order_suborder: # If there is a previous suborder
                return [prev_order_suborder, percentage, order, suborder, prev_suborder_index]
            else: # if there is not a previous suborder
                return None 

        # HELPER FUNCTION    
        def get_ratio_completed_hours_for_suborder(m, i, j):
            """Gets the amount of time that have been completed vs the lowerbound required amount of time. The lowerbound is chosen since using the upperbound could mean that ratio 1 is never reached, however using the lowerbound could mean that ratio 1 is reached prematurely. \n If required time is zero, then the ratio returns 0, because dividing by 0 is impossible.

            Args:
                m (pyo.ConcreteModel()): pyomo model
                i (str): order_suborder index
                j (datetime): time index

            Returns:
                Expression: allocation(sum over {t} if {t} < time j and over employee_line) / time_required_lb
            """
            if time_req_lb.loc[i] == 0:
                return 0
            else:
                ratio = sum(
                    m.var_alloc[(i, ti_j, empl_line_i)]  
                    for ti_j in m.set_time 
                    for empl_line_i in m.set_employee_line
                    if ti_j < j
                    ) / time_req_lb.loc[i] # Total amount of allocated hours of the previous suborder devided by the lowerbound of required time. The lowerbound is taken, since the upperbound could result in the fraction never reaching 1. Opposite of that, lowerbound could mean that the fraction reaches 1 prematurely
            
                return ratio

        # PREVIOUS SUBORDER MUST BE COMPLETED FOR ATLEAST X%
        def rule_prevSuborderCompletedBeforeNext(m, i, j, k):
            """This rule makes sure that before the next suborder is allocated, the previous suborder has to be completed for at least a certain percentage.
            This is done by finding the previous suborder for the order_suborder {i}, then finding the amount of allocated hours before time {j} to the previous suborder
        
            Args:
                m (pyo.ConcreteModel()): pyomo Model
                i (str): order_suborder index
                j (datetime): time index
                k (str): employees_lines index

            Returns:
                Expression: 0 <= allocation <= a, where a >= 0 and 'a >= 1' if enough hours of the previous suborder are completed, else 'a < 1'.
            """
            # Obtain the needed information for the previous suborder.
            list_prev_suborder = get_previous_suborder(i)
            if not list_prev_suborder: # If there is not previous suborder skip the constraint.
                return pyo.Constraint.Skip
            
            percentage = list_prev_suborder[1]
            prev_order_suborder = list_prev_suborder[0]
            
            ratio_completedHoursPrevSuborders = get_ratio_completed_hours_for_suborder(m, prev_order_suborder, j)

            # Dividing by the needed percentage to inflate the completed hours for the previous suborder, such that the restriction is looser if that is allowed. (Elastic constraint?)
            ratio_completed_vs_neededHours = ratio_completedHoursPrevSuborders / percentage

            # The constraint is added for each employee_line since summing over the employee_line {k} would result in unbalanced equation. This causes a possibility that the amount of required hours for the order_suborder is smaller than the RHS, since the LHS sum could then become equal to the required hours the order_suborder could be completed before the other previous suborder is completed.
            return m.var_alloc[i,j,k] <= ratio_completed_vs_neededHours
        self.m.constr_prevSuborderCompletedBeforeNext = pyo.Constraint(self.m.set_order_suborder, self.m.set_time, self.m.set_employee_line, rule=rule_prevSuborderCompletedBeforeNext)

        # PREVIOUS SUBORDER MUST BE COMPLETED FOR A LARGER PERCENTAGE THAN THE NEXT SUBORDER
        def rule_prevSuborderCannotOvertakeCurrentSuborder(m, i, j):
            """This rule makes sure that the current suborder cannot be scheduled for a larger percentage than the previous suborder. This is, you cannot schedule to submit 5 papers, if you have only written 3 papers at time {j}

            Args:
                m (pyo.ConcreteModel()): pyomo Model
                i (str): order_suborder index
                j (datetime): time index
            
            Returns:
                Expression: ratio_previous_suborder >= ratio_current_suborder, for the completed amount of hours vs the required amount per suborder.
            """

            # Obtain the needed information for the previous suborder.
            list_prev_suborder = get_previous_suborder(i)
            if not list_prev_suborder: # If there is not previous suborder skip the constraint.
                return pyo.Constraint.Skip
            
            prev_order_suborder = list_prev_suborder[0]

            # Obtain the ratio's
            ratio_Current = get_ratio_completed_hours_for_suborder(m, i, j)
            ratio_Prev = get_ratio_completed_hours_for_suborder(m, prev_order_suborder, j)

            # If either of the ratios is a pyo.numeric_expr.DivisionExpression, then return the constraint
            if isinstance(ratio_Prev, pyo.numeric_expr.DivisionExpression) or isinstance(ratio_Current, pyo.numeric_expr.DivisionExpression):
                return ratio_Prev >= ratio_Current
            elif ratio_Prev == 0 and ratio_Current == 0: # If both ratios are zero, then skip the constraint.
                return pyo.Constraint.Skip
            else:
                return ratio_Prev >= ratio_Current
        self.m.constr_prevSuborderCannotOvertakeNextSuborder = pyo.Constraint(self.m.set_order_suborder, self.m.set_time, rule=rule_prevSuborderCannotOvertakeCurrentSuborder)
        
        ### RULES THAT IMPLEMENT THAT ORDERS ARE ALLOCATED ONLY TO SPECIFIC (TYPE OF) LINES OF EMPLOYEES.
        # LINE ORDERS ALLOCATED TO LINES
        def rule_lineOrdersOnLine(m, i, k): 
            """This rule makes sure that all order_suborder {i} that should be executed on a line are indeed executed on a line.
            This is done by restricting employees {k}, such that they are not able for allocation on line orders {i}. 

            Args:
                m (pyo.ConcreteModel()): pyomo Model
                i (str): order_suborder index
                k (str): employee index

            Returns:
                Expression: 0 <= allocation(sum over time)(for all employees {k}) <= 0 if order_suborder {i} should be allocated on a line, else constraint is skipped.
            """
            if self.exec_on_line_df.loc[i].iloc[0]: # Check whether an order_suborder should be preformed on a line.
                return (0, sum(m.var_alloc[(i, j, k)] for j in m.set_time), 0)
            else:
                return pyo.Constraint.Skip # Skips the constraint if an order_suborder should not be preformed on a line.
        self.m.constr_lineOrdersOnLine = pyo.Constraint(self.m.set_order_suborder, self.m.set_employee, rule=rule_lineOrdersOnLine)

        # SPECIFIC LINE ORDERS ALLOCATED TO THE SPECIFIC LINE
        def rule_orderOnSpecificLine(m, i, k):
            """This rule makes sure that if an order_suborder {i} should be performed on a specific line. 
            This is done by restricting all employee_line {k} that is unequal to the specific line to zero.

            Args:
                m (pyo.ConcreteModel()): pyomo model
                i (str): order_suborder index
                j (timedate): time index
                k (str): employee_line index

            Returns:
                Expression: 0 <= allocation(sum over time) <= 0, for employee_line {k} if the order_suborder must be allocated by a specific line other than the current employee_line {k}, else the constraint is skipped.
            """
            specific_line = self.specific_line_df.loc[i].iloc[0]
            
            if specific_line != '': # Continue only if the order_suborder {k} has a specific line on which it must be preformed.
                if specific_line != k: # if employee_line {k} is not equal to the specific line
                    return (0, sum(m.var_alloc[(i, j, k)] for j in m.set_time), 0)
            return pyo.Constraint.Skip
        self.m.constr_ordersOnSpecificLine = pyo.Constraint(self.m.set_order_suborder, self.m.set_employee_line, rule=rule_orderOnSpecificLine)

        # MANUAL ORDERS ALLOCATED TO EMPLOYEES
        def rule_manualOrdersForEmployee(m, i, j, k):
            """This rule makes sure that all orders that should be executed by an employee are not executed on a line.
            This is done by restricting lines, such that they are not able for allocation on non line orders. 

            Args:
                m (pyo.ConcreteModel()): pyomo Model
                i (str): order_suborder index
                j (datetime): time index
                k (str): lines index

            Returns:
                Expression: 0 <= allocation(sum over time) <= 0, if order_suborder {i} is not executed on a line (that is, is executed by employees) then the order_suborder cannot be allocated to lines.
            """
            if not self.exec_on_line_df.loc[i].iloc[0]: # If the order_suborder is not executed on a line -> it is executed by employees.
                return (0, m.var_alloc[(i, j, k)], 0)
            else:
                return pyo.Constraint.Skip
        self.m.constr_manualOrdersForEmployee = pyo.Constraint(self.m.set_order_suborder, self.m.set_time, self.m.set_line, rule=rule_manualOrdersForEmployee)

        ### RULES THAT IMPLEMENT THE OLD- AND MANUAL PLANNING.
        # OLD PLANNING
        def rule_oldPlanning(m, i, j, k):
            """This rule makes sure that the old planning from the excelFile is satisfied, only allocations that are before the old_planning_limit are allocated, otherwise the constraint is skipped.

            Args:
                m (pyo.ConcreteModel()): pyomo model
                i (str): order_suborder index
                j (datetime): time index
                k (str): employee_line index

            Returns:
                Expression: new_allocation = old_allocation, if there was an old_allocation that is before the old_planning_limit, else the constraint is skipped.
            """
            if j <= pd.to_datetime(old_planning_limit, format='%d-%m-%Y %H:%M:%S'): # Only take into account the old schedule if the time {j} is smaller than the old_planning_limit, that represents the benchmark until which point the old planning must be taken into account.
                try:
                    if self.old_planning_df.loc[i, j, k] == 1: # If there is an old allocation, then bind the new allocation to the old. 
                        return m.var_alloc[(i, j, k)] == int(self.old_planning_df.loc[i, j, k])
                    else: # If there is no old allocation, skip the constraint. (this can happen when {i} is scheduled, but not at time {j} or by employee_line {k})
                        return pyo.Constraint.Skip
                except: # If there is not value for {i, j, k} in the old planning, then skip the constraint.
                    return pyo.Constraint.Skip
            else:
                return pyo.Constraint.Skip
        #self.m.constr_oldPlanning = pyo.Constraint(self.m.set_order_suborder, self.m.set_time, self.m.set_employee_line, rule=rule_oldPlanning)

        # MANUAL PLANNING
        def rule_manualPlanning(m, i, j, k):
            """This rule makes sure that the manual planning from the ExcelFile is satisfied. This happens for all manual allocations because those are of the highest importance, since they are scheduled by the decision maker. 

            Args:
                m (pyo.ConcreteModel()): pyomo model
                i (str): order_suborder index
                j (datetime): time index
                k (str): employee_line index

            Returns:
                Expression: new_allocation = manual_planning, if there is an manual_allocation. 
            """
            try:
                if self.manual_planning_df.loc[i, j, k] == 1.0: # If there exists a manual_allocation, else skip the constraint. 
                    return m.var_alloc[(i, j, k)] == int(self.manual_planning_df.loc[i, j, k])
                else:
                    return pyo.Constraint.Skip
            except:
                return pyo.Constraint.Skip
        #self.m.constr_manualPlanning = pyo.Constraint(self.m.set_order_suborder, self.m.set_time, self.m.set_employee_line, rule=rule_manualPlanning)

        # COMBINED PLANNING
        def rule_planning(m, i, j, k):
            """This rule makes sure that both the old_ and manual_planning from the ExcelFile are satisfied. 
            That is, manual_allocations and old_allocations are implemented, but only old_allocations if their time {j} is before the old_planning_limit, otherwise the constraint is skipped.
            Here manual_ has a higher importance than old_planning, so that if there is a confict the manual_planning will be chosen. 

            Args:
                m (pyo.ConcreteModel()): pyomo model
                i (str): order_suborder index
                j (datetime): time index
                k (str): employee_line index

            Returns:
                Expression: new_allocation = manual_allocation or old_allocation, if one is present, if both are present the manual_allocation will be followed. Old_allocations will only be implemented if they happen before the old_planning_limit.
            """
            try:
                if self.combined_planning_df.loc[i, j, k] == 1: # If either there is a manual_ or an old_planning present, otherwise skip the constraint.
                    return m.var_alloc[(i, j, k)] == self.combined_planning_df.loc[i, j, k]
                else:
                    return pyo.Constraint.Skip
            except:
                return pyo.Constraint.Skip
        self.m.constr_planning = pyo.Constraint(self.m.set_order_suborder, self.m.set_time, self.m.set_employee_line, rule=rule_planning)

        ### RULES THAT IMPLEMENT THE GAPS IDENTIFICATION.

        ## DIFFERENCE BETWEEN BEFORE AND AFTER IS IN THE SECOND SUMMATION, THAT IS T <=/>= J (BEFORE/AFTER). 
        # BEFORE INDICATES IF THE ORDER_SUBORDER HAS BEEN ALLOCATED BEFORE SPECIFIC TIME
        def rule_gaps_before1(m, i, j):
            """This rule is part of the 'gaps before constraints' series, that indicates when an order_suborder {i} has been allocated before/during a particular time {j}. 
            
            This specific rule makes sure that:
            2 * [ allocation(sum over time {t} if t <= time {j} and over employee_line) ] - 1 <= upperbound * var_before
                More specifically:
                    if [ allocation(sum over time {t} if t <= time {j} and over employee_line) ] >= 1
                    then var_before = 1

            Args:
                m (pyo.ConcreteModel()): pyomo model
                i (str): order_suborder index
                j (datetime): time index

            Returns:
                Expression: 2 * [ allocation(sum over time {t} if t <= time {j} and over employee_line) ] - 1 <= upperbound * var_before
            """
            try:
                return 2 * sum(
                                sum(
                                    m.var_alloc[(i, t, k)] 
                                    for k in m.set_employee_line
                                    ) 
                                for t in m.set_time 
                                if t <= j
                    ) - 1 <= m.upperbound_of_employees_and_time * m.var_before[(i, j)]
            except:
                return pyo.Constraint.Skip
        self.m.gaps_before1 = pyo.Constraint(self.m.set_order_suborder, self.m.set_time, rule=rule_gaps_before1)

        def rule_gaps_before2(m, i, j):
            """This rule is part of the 'gaps before constraints' series, that indicates when an order_suborder has been allocated before/during a particular time. 
            
            This specific rule makes sure that:
            var_before <= [ allocation(sum over time {t} if t <= time {j} and over employee_line) ]
                More specifically: if [ allocation(sum over time {t} if t <= time {j} and over employee_line) ] <= 0 -> var_before = 0

            Args:
                m (pyo.ConcreteModel()): pyomo model
                i (str): order_suborder index
                j (datetime): time index

            Returns:
                Expression: var_before <= [ allocation(sum over time {t} if t <= time {j} and over employee_line) ]
            """
            try:
                return m.var_before[(i, j)] <= sum(
                                                sum(m.var_alloc[(i, t, k)] 
                                                    for k in m.set_employee_line
                                                    ) 
                                                for t in m.set_time 
                                                if t <= j
                                                )
            except:
                return pyo.Constraint.Skip
        self.m.gaps_before2 = pyo.Constraint(self.m.set_order_suborder, self.m.set_time, rule=rule_gaps_before2)

        # AFTER INDICATES IF THE ORDER_SUBORDER HAS BEEN ALLOCATED AFTER A SPECIFIC TIME
        def rule_gaps_after1(m, i, j):
            """This rule is part of the 'gaps after constraints' series, that indicates when an order_suborder {i} has been allocated after/during a particular time {j}. 
            
            This specific rule makes sure that:
            2 * [ allocation(sum over time {t} if t >= time {j} and over employee_line) ] - 1 <= upperbound * var_after
                More specifically:
                    if [ allocation(sum over time {t} if t >= time {j} and over employee_line) ] >= 1
                    then var_after = 1

            Args:
                m (pyo.ConcreteModel()): pyomo model
                i (str): order_suborder index
                j (datetime): time index

            Returns:
                Expression: 2 * [ allocation(sum over time {t} if t >= time {j} and over employee_line) ] - 1 <= upperbound * var_after
            """
            try:
                return 2 * sum(
                                sum(
                                    m.var_alloc[(i, t, k)] 
                                    for k in m.set_employee_line
                                    ) 
                                for t in m.set_time 
                                if t >= j
                    ) - 1 <= m.upperbound_of_employees_and_time * m.var_after[(i, j)]
            except:
                return pyo.Constraint.Skip
        self.m.gaps_after1 = pyo.Constraint(self.m.set_order_suborder, self.m.set_time, rule=rule_gaps_after1)

        def rule_gaps_after2(m, i, j):
            """This rule is part of the 'gaps after constraints' series, that indicates when an order_suborder has been allocated after/during a particular time. 
            
            This specific rule makes sure that:
            var_after <= [ allocation(sum over time {t} if t >= time {j} and over employee_line) ]
                More specifically: 
                    if [ allocation(sum over time {t} if t >= time {j} and over employee_line) ] <= 0 
                    then var_after = 0

            Args:
                m (pyo.ConcreteModel()): pyomo model
                i (str): order_suborder index
                j (datetime): time index

            Returns:
                Expression: var_before <= [ allocation(sum over time {t} if t >= time {j} and over employee_line) ]
            """
            try:
                return m.var_after[(i, j)] <= sum(
                                                sum(m.var_alloc[(i, t, k)] 
                                                    for k in m.set_employee_line
                                                    ) 
                                                for t in m.set_time 
                                                if t >= j
                                                )
            except:
                return pyo.Constraint.Skip
        self.m.gaps_after2 = pyo.Constraint(self.m.set_order_suborder, self.m.set_time, rule=rule_gaps_after2)

        # DURING INDICATES IF AT A CERTAIN TIME THE ORDER HAS BEEN STARTED AND HAS NOT YET BEEN FINISHED, THUS INDICATES ALL TIME INTERVALS BETWEEN START AND FINISH OF ORDER
        def rule_gaps_during1(m, i, j):
            """This rule is part of the 'gaps during constraints' series, that indicate the time intervals where an order_suborder has been started, but not yet finished. This is between the start and finish allocation of an order.

            This specific rule makes sure that:
            var_during <= var_before
                More specifically:
                    if var_before = 0
                    then var_during = 0

            Args:
                m (pyo.ConcreteModel()): pyomo model
                i (str): order_suborder index
                j (datetime): time index

            Returns:
                Expression: var_during <= var_before
            """
            try:
                return m.var_during[(i, j)] <= m.var_before[(i, j)]
            except:
                return pyo.Constraint.Skip
        self.m.gaps_during1 = pyo.Constraint(self.m.set_order_suborder, self.m.set_time, rule=rule_gaps_during1)

        def rule_gaps_during2(m, i, j):
            """This rule is part of the 'gaps during constraints' series, that indicate the time intervals where an order_suborder has been started, but not yet finished. This is between the start and finish allocation of an order.

            This specific rule makes sure that:
            var_during <= var_after
                More specifically:
                    if var_after = 0
                    then var_during = 0

            Args:
                m (pyo.ConcreteModel()): pyomo model
                i (str): order_suborder index
                j (datetime): time index

            Returns:
                Expression: var_during <= var_after
            """
            try:
                return m.var_during[(i, j)] <= m.var_after[(i, j)]
            except:
                return pyo.Constraint.Skip
        self.m.gaps_during2 = pyo.Constraint(self.m.set_order_suborder, self.m.set_time, rule=rule_gaps_during2)

        def rule_gaps_during3(m, i, j):
            """This rule is part of the 'gaps during constraints' series, that indicate the time intervals where an order_suborder has been started, but not yet finished. This is between the start and finish allocation of an order.

            This specific rule makes sure that:
            var_during >= var_before + var_after - 1
                More specifically:
                    if either var_before = 1 or var_after = 1
                    then var_during = 1

            Args:
                m (pyo.ConcreteModel()): pyomo model
                i (str): order_suborder index
                j (datetime): time index

            Returns:
                Expression: var_during >= var_before + var_after - 1
            """
            try:
                return m.var_during[(i, j)] >= m.var_before[(i, j)] + m.var_after[(i, j)] - 1
            except:
                return pyo.Constraint.Skip
        self.m.gaps_during3 = pyo.Constraint(self.m.set_order_suborder, self.m.set_time, rule=rule_gaps_during3)

        # GAPS INDICATES IF BETWEEN THE START AND FINISH TIMES OF AN ORDER_SUBORDER, THE IS AN NOT ALLOCATION AT A CERTAIN TIME. THAT IS, THERE IS A GAP IN THE SCHEDULE. 
        def rule_gaps_gaps1(m, i, j):
            """This rule is part of the 'gaps constraints' series, that indicate the time intervals where the order_sub has not been allocated, but has been started, but not yet finished. 

            This specific rule makes sure that:
            allocation(sum over employee_line) <= upperbound * var_indicator_alloc_sum_employee_line
                More specifically:
                    if allocation(sum over employee_line) >= 1, that is at least one employee_line is allocated
                    then var_indicator_alloc_sum_employee_line = 1

            Args:
                m (pyo.ConcreteModel()): pyomo model
                i (str): order_suborder index
                j (datetime): time index

            Returns:
                Expression: allocation(sum over employee_line) <= upperbound * var_indicator_alloc_sum_employee_line
            """
            try:
                return sum(m.var_alloc[(i, j, k)] for k in m.set_employee_line) <= m.upperbound_of_employee * m.var_indicator_alloc_sum_employee_line[(i, j)] # m.var_during[(i, j)] - sum(m.var_alloc[(i, k, j)] for k in m.set_employee_line) <= m.upperbound_of_employee * m.var_gaps[(i, j)]
            except:
                return pyo.Constraint.Skip
        self.m.gaps_gaps1 = pyo.Constraint(self.m.set_order_suborder, self.m.set_time, rule=rule_gaps_gaps1)
            
        def rule_gaps_gaps2(m, i, j):
            """This rule is part of the 'gaps constraints' series, that indicate the time intervals where the order_sub has not been allocated, but has been started, but not yet finished. 

            This specific rule makes sure that:
            allocation(sum over employee_line) >= var_indicator_alloc_sum_employee_line
                More specifically:
                    if allocation(sum over employee_line) = 0
                    then var_indicator_alloc_sum_employee_line = 0

            Args:
                m (pyo.ConcreteModel()): pyomo model
                i (str): order_suborder index
                j (datetime): time index

            Returns:
                Expression: allocation(sum over employee_line) >= var_indicator_alloc_sum_employee_line
            """
            try:
                return sum(m.var_alloc[(i, j, k)] for k in m.set_employee_line) >= m.varvar_indicator_alloc_sum_employee_line_z[(i, j)] #m.var_during[(i, j)] - sum(m.var_alloc[(i, k, j)] for k in m.set_employee_line) >= 1 - m.upperbound_of_employee * (1 - m.var_gaps[(i, j)])
            except:
                return pyo.Constraint.Skip
        self.m.gaps_gaps2 = pyo.Constraint(self.m.set_order_suborder, self.m.set_time, rule=rule_gaps_gaps2)

        def rule_gaps_gaps3(m, i, j):
            """This rule is part of the 'gaps constraints' series, that indicate the time intervals where the order_sub has not been allocated, but has been started, but not yet finished. 

            This specific rule makes sure that:
            var_gaps = var_during - var_indicator_alloc_sum_employee_line
                More specifically:
                    if var_during = var_indicator_alloc_sum_employee_line
                    then var_gaps = 0
                    elif var_during > var_indicator_alloc_sum_employee_line # Note, var_during >= var_indicator_alloc_sum_employee_line always holds.
                    then var_gaps = 1

            Args:
                m (pyo.ConcreteModel()): pyomo model
                i (str): order_suborder index
                j (datetime): time index

            Returns:
                Expression: var_gaps = var_during - var_indicator_alloc_sum_employee_line
            """
            try:
                return m.var_gaps[(i, j)] == m.var_during[(i, j)] - m.var_indicator_alloc_sum_employee_line[(i, j)] 
            except:
                return pyo.Constraint.Skip
        self.m.gaps_gaps3 = pyo.Constraint(self.m.set_order_suborder, self.m.set_time, rule=rule_gaps_gaps3)

        self.model_created = True
        
    def solve(self, solver_options=None): 
        """This function solves the previously created problem. 

        Args:
            solver_options (**kwargs, optional): List of options for the solver. Defaults to None.

        Returns:
            output: Output of the solver.
        """
        
        # Check whether the model has been formulated
        if not self.model_created: 
            import sys
            print("Model has not yet been created, that is no variables or constraints are added yet, beefore .solve() is called. ")
            # Or raise ValueError()
            sys.exit()
            

        solver = pyo.SolverFactory('cbc')

        # Set solver options if provided, such as solving time limit.
        if solver_options:
            for option, value in solver_options.items():
                solver.options[option] = value

        # Solve the problem
        results = solver.solve(self.m)
        print(results)
        
        ### Turn the results into observable objects
        solution_values = {(i, j, k): self.m.var_alloc[i, j, k].value for (i, j, k) in self.m.set_alloc_index}

        index_values = [idx for idx in self.m.set_alloc_index]
        index_names = ['order_suborder', 'time', 'empl_line']
        column_names = ['order_suborder']

        optimal_df = pd.Series(solution_values.values(), index=pd.MultiIndex.from_tuples(index_values, names=index_names))
        #optimal_df = optimal_df.groupby(['time', 'order_suborder', 'empl_line'])

        ### Obtain a short version of the solutions.
        self.solution = optimal_df
        self.short_solution = self.solution.copy()[(self.solution!=0)]#.any(axis=1)] # Only keep rows which have non zero values -> an allocation.
        self.short_solution.name = 'allocation'

        # Create the corresponding 'Dataframe' object, and change the corresponding pandas_dataframe.
        self.shortSolution = Dataframe(pandas_excel_file=self.excel_file, dataframe_name='solution_df', excel_sheet_name=dfs.get('solution_df')[0])
        self.shortSolution.change_pandas_dataframe(self.short_solution)

        print(self.short_solution)

        # Obtain a dataframe with the gaps in the planning.
        gap_values = {(i, j): self.m.var_gaps[(i, j)].value for (i, j) in self.m.set_gaps_index}
        index_values = [idx for idx in self.m.set_gaps_index]

        gaps_df = pd.Series(gap_values.values(), index=pd.MultiIndex.from_tuples(index_values, names=['order_suborder', 'time']))
        gaps_df = gaps_df[(gaps_df!=0)]
        gaps_df.name = 'gaps'
        print(gaps_df)

        return results
    
    #FIXME:
    """def test_solvability(self):
        testplanning = TestPlanningEW(self)
        testplanning.checkAll()"""

    def export(self):
        """Exports the short solution to excel.
        """
        self.shortSolution.write_excel_dataframe()

