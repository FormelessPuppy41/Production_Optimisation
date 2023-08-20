import pyomo
import pyomo.opt
import pyomo.environ as pyo
import pandas as pd
import logging

from data.dataframe import Dataframe
from data.dataframes import Dataframes
from data.data_index import Data_Index

from general_configuration import dfs, old_planning_limit

class EWOptimisation:
    """This class implements the optimisation problem for EW.
    """
    def __init__(self, dataframes_class: Dataframes):
        self.dataframes_class = dataframes_class
        self.data_index = Data_Index(self.dataframes_class)
        self.excel_file = dataframes_class.get_dataframe_by_index(0).get_excel_file()

        self.solution = pd.DataFrame
        self.short_solution = pd.DataFrame
        
    
    def createModel(self):
        self.m = pyo.ConcreteModel()

        # Retrieving data
        self.list_order_suborder = self.data_index.get_index_set('order_suborder')
        self.list_suborder_set = self.data_index.get_index_set('suborder')
        self.list_time = self.data_index.get_index_set('time')
        self.list_employee_line = self.data_index.get_index_set('employee_line')
        self.list_employee = self.data_index.get_index_set('employee')
        self.list_line = self.data_index.get_index_set('line')

        dates_df = self.dataframes_class.get_dataframe_by_name('dates_df').get_pandas_dataframe()
        revenue_df = self.dataframes_class.get_dataframe_by_name('revenue_df').get_pandas_dataframe()
        time_req_df = self.dataframes_class.get_dataframe_by_name('time_req_df').get_pandas_dataframe()

        date_start = dates_df.iloc[:, 0]
        date_deadline = dates_df.iloc[:, 1]
        revenue = revenue_df.iloc[:, 0]
        time_req_lb = time_req_df.iloc[:, 0]
        time_req_ub = time_req_df.iloc[:, 1]

        skills_df = self.dataframes_class.get_dataframe_by_name('skills_df').get_pandas_dataframe()
        availability_df = self.dataframes_class.get_dataframe_by_name('availability_df').get_pandas_dataframe()
        specific_order_suborder = self.dataframes_class.get_dataframe_by_name('order_specific_df').get_pandas_dataframe()
        exec_on_line_df = self.dataframes_class.get_dataframe_by_name('line_indicator_df').get_pandas_dataframe()
        penalty_df = self.dataframes_class.get_dataframe_by_name('penalty_df').get_pandas_dataframe()
        suborders_df = self.dataframes_class.get_dataframe_by_name('next_prev_suborder_df').get_pandas_dataframe()
        percentage_df = self.dataframes_class.get_dataframe_by_name('percentage_df').get_pandas_dataframe()
        old_planning_df = self.dataframes_class.get_dataframe_by_name('old_planning_df').get_pandas_dataframe()
        manual_planning_df = self.dataframes_class.get_dataframe_by_name('manual_planning_df').get_pandas_dataframe()

        # Dataframe where unique_code can be looked for by using specific order and suborder.
        transpose_specific_order_suborder = specific_order_suborder.copy()
        transpose_index = specific_order_suborder.columns.to_list()
        transpose_specific_order_suborder.reset_index(inplace=True)
        transpose_specific_order_suborder.set_index(transpose_index, inplace=True)

        # Create sets
        self.m.set_order_suborder = pyo.Set(initialize=self.list_order_suborder)
        self.m.set_time = pyo.Set(initialize=self.list_time)
        self.m.set_employee_line = pyo.Set(initialize=self.list_employee_line)
        self.m.set_employee = pyo.Set(initialize=self.list_employee)
        self.m.set_line = pyo.Set(initialize=self.list_line)
        
        self.m.set_alloc_index = pyo.Set(initialize=self.m.set_order_suborder * self.m.set_time * self.m.set_employee_line)
        self.upperbound = len(self.m.set_order_suborder)*len(self.m.set_time)*len(self.m.set_employee_line)
    
        # Create variables
        self.m.var_alloc = pyo.Var(self.m.set_alloc_index, domain=pyo.Binary)

        
        # Create objective
        def rule_objectiveFunction(m):
            penalty = sum(
                m.var_alloc[i, j, k] * penalty_df.loc[j, i]
                for i in m.set_order_suborder
                for j in m.set_time
                for k in m.set_employee_line
                )
            return penalty
        self.m.objectiveFunction = pyo.Objective(rule=rule_objectiveFunction(self.m), sense=pyo.minimize)

        # Create Constraints
        def rule_requiredPlannedHours(m, i):
            """Makes sure all orders meet their required amount of planned hours, that is it's lower and upperbound 
            
            Note: The sum in the restriction gives the total amound of planned hours per order.

            Args:
                m (Pyomo Model): Model
                i (str): Order index

            Returns:
                Expression: time_req_lb <= sum over time and employees and or lines for allocation <= req_time_up
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


        def rule_oneAllocPerEmpl_linePerMoment(m, j, k):
            """This rule makes sure that at any given moment every employee and/or line {k} is allocated a maximum of one time.

            Args:
                m (Model): Pyomo model
                j (Time): Time interval
                k (empl_line): Employees and/or Lines

            Returns:
                Expression: 0 <= sum over order_suborder's for allocation <= 1
            """
            return (
                0, 
                sum(m.var_alloc[(i, j, k)]
                    for i in m.set_order_suborder
                ),
                1
            )
        self.m.constr_oneAllocPerEmpl_linPerMoment = pyo.Constraint(self.m.set_time, self.m.set_employee_line, rule=rule_oneAllocPerEmpl_linePerMoment)


        def rule_onlyAllocIfEmpl_lineSkilled(m, i, j, k):
            """This rule makes sure that an employee and or line can only be allocated to a suborder if it is skilled to do so.

            Args:
                m (Model): Pyomo Model
                i (order_suborder): Order_suborder
                j (Time): Time intervals
                k (empl_line): Employees and/or Lines

            Returns:
                Expression: 0 <= allocation <= 1 (skills_df has value of either 0 or 1)
            """
            suborder = specific_order_suborder.loc[i].iloc[1]
            return (0, 
                    m.var_alloc[(i, j, k)], 
                    skills_df.loc[k, suborder]) #FIXME: During cleaning every none value should be changed to a 0 value. 
        self.m.constr_onlyAllocIfEmpl_lineSkilled = pyo.Constraint(self.m.set_order_suborder, self.m.set_time, self.m.set_employee_line, rule= rule_onlyAllocIfEmpl_lineSkilled)
    

        def rule_onlyAllocIfEmpl_lineAvailable(m, i, j, k):
            """This rule makes sure that an employee and or line can only be allocated on a time interval if they are available to do so.

            Args:
                m (Model): Pyomo Model
                i (order_suborder): Order_suborder
                j (Time): Time intervals
                k (empl_line): Employees and/or Lines

            Returns:
                Expression: 0 <= allocation <= 1 (availability_df has value of either 0 or 1)
            """
            return (0, 
                    m.var_alloc[(i, j, k)], 
                    availability_df.loc[j, k]) #FIXME: During cleaning every none value should be changed to a 0 value. 
        self.m.constr_onlyAllocIfEmpl_lineAvailable = pyo.Constraint(self.m.set_order_suborder, self.m.set_time, self.m.set_employee_line, rule= rule_onlyAllocIfEmpl_lineAvailable)
    

        def rule_prevSuborderCompletedBeforeNext(m, i, j, k):
            """This rule makes sure that before the next suborder is allocated, the previous suborder has to be completed.

            Args:
                m (Model): Pyomo Model
                i (order_suborder): Order_suborder
                j (Time): Time intervals
                k (empl_line): Employees and/or Lines

            Returns:
                Expression: 0 <= allocation <= a, where a >= 0 and a>= 1 if enough hours of the previous suborder are completed. 
            """
            order = specific_order_suborder.loc[i].iloc[0]
            suborder = specific_order_suborder.loc[i].iloc[1]
            percentage = percentage_df.loc[i].iloc[0]

            prev_suborder_index = self.list_suborder_set.index(suborder) - 1

            while prev_suborder_index > 0:
                prev_suborder = self.list_suborder_set[prev_suborder_index]
                try:
                    prev_order_suborder = transpose_specific_order_suborder.loc[order, prev_suborder].iloc[0]
                    break # valid suborder found
                except KeyError:
                    prev_suborder_index -= 1
                    continue

            if prev_suborder_index <= 0:
                return pyo.Constraint.Skip
            
            ratio_completedHoursPrevSuborders = sum(
                m.var_alloc[(prev_order_suborder, ti_j, empl_line_i)]/time_req_lb.loc[prev_order_suborder]  
                for ti_j in m.set_time 
                for empl_line_i in m.set_employee_line
                if ti_j < j
            )

            ratio_completed_vs_neededHours = ratio_completedHoursPrevSuborders / percentage

            #TODO: The current structure loops through every possiblitiy instead of grabbing a specific order_suborder combination that is being implicated via suborders_df (prev/next_suborder)
            #TODO: Add constraint that makes sure that there is never scheduled 'more' of next suborder then previous, that is mont cannot be fully scheduled if previous smd2 is not fully scheduled.

            return m.var_alloc[i,j,k] <= ratio_completed_vs_neededHours
        self.m.constr_prevSuborderCompletedBeforeNext = pyo.Constraint(self.m.set_order_suborder, self.m.set_time, self.m.set_employee_line, rule=rule_prevSuborderCompletedBeforeNext)

    
        def rule_lineOrdersOnLine(m, i, j, k): 
            """Makes sure that all orders that should be executed on a line are indeed executed on a line.
            This is done by restricting employees, such that they are not able for allocation on line orders. 

            Args:
                m (Model): Pyomo Model
                i (Order_suborder): order_suborder set
                j (Time): time interval set
                k (Employees): employee set

            Returns:
                Expression: Employees can't be allocated on line orders.
            """
            if exec_on_line_df.loc[i].iloc[0]:
                return (0, m.var_alloc[(i, j, k)], 0)
            else:
                return pyo.Constraint.Skip
        self.m.constr_lineOrdersOnLine = pyo.Constraint(self.m.set_order_suborder, self.m.set_time, self.m.set_employee, rule=rule_lineOrdersOnLine)


        def rule_manualOrdersForEmployee(m, i, j, k):
            """Makes sure that all orders that should not be executed on a line are not executed on a line.
            This is done by restricting lines, such that they are not able for allocation on non line orders. 

            Args:
                m (Model): Pyomo Model
                i (Order_suborder): order_suborder set
                j (Time): time interval set
                k (Lines): lines set

            Returns:
                Expression: lines can't be allocated on non line orders.
            """
            if not exec_on_line_df.loc[i].iloc[0]:
                return (0, m.var_alloc[(i, j, k)], 0)
            else:
                return pyo.Constraint.Skip
        self.m.constr_manualOrdersForEmployee = pyo.Constraint(self.m.set_order_suborder, self.m.set_time, self.m.set_line, rule=rule_manualOrdersForEmployee)

        def rule_oldPlanning(m, i, j, k):
            if j <= pd.to_datetime(old_planning_limit, format='%d-%m-%Y %H:%M:%S'):
                try:
                    if old_planning_df.loc[i, j, k] == 1:
                        #print(old_planning_df)
                        return m.var_alloc[(i, j, k)] == int(old_planning_df.loc[i, j, k])
                    else:
                        return pyo.Constraint.Skip
                except:
                    return pyo.Constraint.Skip
            else:
                return pyo.Constraint.Skip
        self.m.constr_oldPlanning = pyo.Constraint(self.m.set_order_suborder, self.m.set_time, self.m.set_employee_line, rule=rule_oldPlanning)

        def rule_manualPlanning(m, i, j, k):
            try:
                if manual_planning_df.loc[i, j, k] == 1.0:
                    #print(manual_planning_df)
                    #print(int(manual_planning_df.loc[i, j, k]))
                    #print('waw')
                    return m.var_alloc[(i, j, k)] == int(manual_planning_df.loc[i, j, k])
                else:
                    return pyo.Constraint.Skip
            except:
                return pyo.Constraint.Skip
        self.m.constr_manualPlanning = pyo.Constraint(self.m.set_order_suborder, self.m.set_time, self.m.set_employee_line, rule=rule_manualPlanning)

    def solve(self, solver_options=None): #FIXME: Problem is with multiple constraints for the same index combination in manual and old planning => contraciting values. Because only executing one or the other does work. Possibly make it the same as the checkers of planning data from excel, that is, 
        #loop through the indexes of the df's and only execute if present or use one constraint with the concatenated dataframe of the two, this way only one constraint is build for each index. BUT this does give into complications with the restrictionline of old planning, but it is possible to filter filter oldplanning based on that criterea. and then concatenate
        solver = pyo.SolverFactory('cbc')

        # Set solver options if provided
        if solver_options:
            for option, value in solver_options.items():
                solver.options[option] = value

        results = solver.solve(self.m)
        print(results)

        solution_values = {(i, j, k): self.m.var_alloc[i, j, k].value for (i, j, k) in self.m.set_alloc_index}

        index_values = [idx for idx in self.m.set_alloc_index]
        index_names = ['order_suborder', 'time', 'empl_line']
        column_names = ['order_suborder']

        optimal_df = pd.Series(solution_values.values(), index=pd.MultiIndex.from_tuples(index_values, names=index_names))
        #optimal_df = optimal_df.groupby(['time', 'order_suborder', 'empl_line'])
        self.solution = optimal_df
        self.short_solution = self.solution.copy()[(self.solution!=0)]#.any(axis=1)]

        self.shortSolution = Dataframe(pandas_excel_file=self.excel_file, dataframe_name='solution_df', excel_sheet_name=dfs.get('solution_df')[0])
        self.shortSolution.change_pandas_dataframe(self.short_solution)

        print(self.short_solution)
        return results
    
    def export(self):
        self.shortSolution.write_excel_dataframe()


