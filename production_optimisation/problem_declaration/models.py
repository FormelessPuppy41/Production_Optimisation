import pyomo
import pyomo.opt
import pyomo.environ as pyo
import pandas as pd
import logging

from data.dataframe import Dataframe
from data.dataframes import Dataframes
from data.data_index import Data_Index

from general_configuration import dfs, old_planning_limit

""" 
Aks in ChatGPT:
how to keep your complicated pyomo project organised, that is if i use variables and sets then i define them as: self.m.var/set because of this i cannot autocomplete or get recommendations for arguments inside the var/set. If i work in a large project this results in difficulties keeping track of the correct indexes and var/set names. How can i overcome this difficulty?

What if we make it a shortest path problem. minimizing the maximum length of each order with a non specified starting point.
That is you apply the A* algorithm to the optimisation. with length of the needed time to complete. https://www.youtube.com/watch?v=A60q6dcoCjw
This way you first minimize the actual schedule before assigning the specific jobs to people. It still remains to find a way to have correct lengths for the jobs without being able to differentiate a hour having one worker or multiple work on the project and thus reducing the length. 
"""

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
        specific_line_df = self.dataframes_class.get_dataframe_by_name('specific_line_df').get_pandas_dataframe()
        exec_on_line_df = self.dataframes_class.get_dataframe_by_name('line_indicator_df').get_pandas_dataframe()
        penalty_df = self.dataframes_class.get_dataframe_by_name('penalty_df').get_pandas_dataframe()
        suborders_df = self.dataframes_class.get_dataframe_by_name('next_prev_suborder_df').get_pandas_dataframe()
        percentage_df = self.dataframes_class.get_dataframe_by_name('percentage_df').get_pandas_dataframe()
        old_planning_df = self.dataframes_class.get_dataframe_by_name('old_planning_df').get_pandas_dataframe()
        manual_planning_df = self.dataframes_class.get_dataframe_by_name('manual_planning_df').get_pandas_dataframe()
        combined_planning_df = self.dataframes_class.get_dataframe_by_name('old_and_manual_planning_df').get_pandas_dataframe()

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
        self.m.set_gaps_index = pyo.Set(initialize=self.m.set_order_suborder * self.m.set_time)

        # Upperbounds
        self.upperbound = len(self.m.set_order_suborder) * len(self.m.set_time) * len(self.m.set_employee_line)
        self.m.upperbound_of_employee = len(self.m.set_employee_line)
        self.m.upperbound_of_employees_and_time = len(self.m.set_employee_line) * len(self.m.set_time)
    
        # Create variables
        self.m.var_alloc = pyo.Var(self.m.set_alloc_index, domain=pyo.Binary)

        # Binary variables
        self.m.var_before = pyo.Var(self.m.set_gaps_index, domain=pyo.Binary)
        self.m.var_after = pyo.Var(self.m.set_gaps_index, domain=pyo.Binary)
        self.m.var_during = pyo.Var(self.m.set_gaps_index, domain=pyo.Binary)
        self.m.var_gaps = pyo.Var(self.m.set_gaps_index, domain=pyo.Binary)

        
        # Create objective
        def rule_objectiveFunction(m):
            penalty = sum(
                m.var_alloc[i, j, k] * penalty_df.loc[j, i]
                for i in m.set_order_suborder
                for j in m.set_time
                for k in m.set_employee_line
                ) + sum(
                    m.var_during[(i, j)] * 400 #FIXME: should be m.var_gaps, but first fix the fixme at line 396. 
                    for i in m.set_order_suborder
                    for j in m.set_time
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


        def rule_orderOnSpecificLine(m, i, j, k):
            specific_line = specific_line_df.loc[i].iloc[0]
            
            if specific_line != '':
                if specific_line != k:
                    return (0, m.var_alloc[(i, j, k)], 0)
            return pyo.Constraint.Skip
        self.m.constr_ordersOnSpecificLine = pyo.Constraint(self.m.set_order_suborder, self.m.set_time, self.m.set_employee_line, rule=rule_orderOnSpecificLine)


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
        #self.m.constr_oldPlanning = pyo.Constraint(self.m.set_order_suborder, self.m.set_time, self.m.set_employee_line, rule=rule_oldPlanning)

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
        #self.m.constr_manualPlanning = pyo.Constraint(self.m.set_order_suborder, self.m.set_time, self.m.set_employee_line, rule=rule_manualPlanning)

        def rule_planning(m, i, j, k):
            try:
                if combined_planning_df.loc[i, j, k] == 1:
                    return m.var_alloc[(i, j, k)] == combined_planning_df.loc[i, j, k]
                else:
                    return pyo.Constraint.Skip
            except:
                return pyo.Constraint.Skip
        self.m.constr_planning = pyo.Constraint(self.m.set_order_suborder, self.m.set_time, self.m.set_employee_line, rule=rule_planning)

        # Identifying gaps in the planning. Difference between before and after is in the second summations, that is t <=/>= j. 
        def rule_gaps_before1(m, i, j):
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

        def rule_gaps_after1(m, i, j): #FIXME: Makes the model infeasable. 
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

        # During indicates all the TI between and including the start and end TI of an order. 
        #FIXME: could it not also happen with: x1i + x2i >= 1 + yi, yi = 1 if x1i=x2i=1 else 0 
        def rule_gaps_during1(m, i, j):
            try:
                return m.var_during[(i, j)] <= m.var_before[(i, j)]
            except:
                return pyo.Constraint.Skip
        self.m.gaps_during1 = pyo.Constraint(self.m.set_order_suborder, self.m.set_time, rule=rule_gaps_during1)

        def rule_gaps_during2(m, i, j):
            try:
                return m.var_during[(i, j)] <= m.var_after[(i, j)]
            except:
                return pyo.Constraint.Skip
        self.m.gaps_during2 = pyo.Constraint(self.m.set_order_suborder, self.m.set_time, rule=rule_gaps_during2)

        def rule_gaps_during3(m, i, j):
            try:
                return m.var_during[(i, j)] >= m.var_before[(i, j)] + m.var_after[(i, j)] - 1
            except:
                return pyo.Constraint.Skip
        self.m.gaps_during3 = pyo.Constraint(self.m.set_order_suborder, self.m.set_time, rule=rule_gaps_during3)

        # Gaps is a variable that shows on which TI's the order is not being executed, while it being past the begin TI and before the End TI. 
        def rule_gaps_gaps1(m, i, j):
            try:
                return m.var_during[(i, j)] - sum(m.var_alloc[(i, k, j)] for k in m.set_employee_line) <= m.upperbound_of_employee * m.var_gaps[(i, j)]
            except:
                return pyo.Constraint.Skip
        self.m.gaps_gaps1 = pyo.Constraint(self.m.set_order_suborder, self.m.set_time, rule=rule_gaps_gaps1)
            
        def rule_gaps_gaps2(m, i, j):
            try:
                return m.var_during[(i, j)] - sum(m.var_alloc[(i, k, j)] for k in m.set_employee_line) >= 1 - m.upperbound_of_employee * (1 - m.var_gaps[(i, j)])
            except:
                return pyo.Constraint.Skip
        self.m.gaps_gaps2 = pyo.Constraint(self.m.set_order_suborder, self.m.set_time, rule=rule_gaps_gaps2)
        

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
        self.short_solution.name = 'allocation'

        self.shortSolution = Dataframe(pandas_excel_file=self.excel_file, dataframe_name='solution_df', excel_sheet_name=dfs.get('solution_df')[0])
        self.shortSolution.change_pandas_dataframe(self.short_solution)

        print(self.short_solution)

        gap_values = {(i, j): self.m.var_gaps[(i, j)].value for (i, j) in self.m.set_gaps_index}
        index_values = [idx for idx in self.m.set_gaps_index]

        gaps_df = pd.Series(gap_values.values(), index=pd.MultiIndex.from_tuples(index_values, names=['order_suborder', 'time']))
        gaps_df = gaps_df[(gaps_df!=0)]
        gaps_df.name = 'gaps'
        print(gaps_df)


        return results
    
    def export(self):
        self.shortSolution.write_excel_dataframe()


