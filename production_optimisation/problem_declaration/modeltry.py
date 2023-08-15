import pyomo
import pyomo.opt
import pyomo.environ as pyo
import pandas as pd
import logging

from data.dataframes import Dataframes
from data.data_index import Data_Index

from general_configuration import all_dataframes

class EWOptimisation:
    """This class implements the optimisation problem for EW.
    """
    def __init__(self, dataframes_class: Dataframes):
        self.dataframes_class = dataframes_class
        self.data_index = Data_Index(self.dataframes_class)
        

    
    def createModel(self):
        self.m = pyo.ConcreteModel()

        # Retrieving data
        order_suborder = self.data_index.get_index_set('order_suborder')
        suborder_set = self.data_index.get_index_set('suborder')
        time = self.data_index.get_index_set('time')
        employee_line = self.data_index.get_index_set('employee_line')
        employee = self.data_index.get_index_set('employee')
        line = self.data_index.get_index_set('line')

        dates_df = self.dataframes_class.get_dataframe_by_name(all_dataframes.get('dates_df')).get_pandas_dataframe()
        revenue_df = self.dataframes_class.get_dataframe_by_name(all_dataframes.get('revenue_df')).get_pandas_dataframe()
        time_req_df = self.dataframes_class.get_dataframe_by_name(all_dataframes.get('time_req_df')).get_pandas_dataframe()

        date_start = dates_df.iloc[:, 0]
        date_deadline = dates_df.iloc[:, 1]
        revenue = revenue_df.iloc[:, 0]
        time_req_lb = time_req_df.iloc[:, 0]
        time_req_ub = time_req_df.iloc[:, 1]

        skills_df = self.dataframes_class.get_dataframe_by_name(all_dataframes.get('skills_df')).get_pandas_dataframe()
        availability_df = self.dataframes_class.get_dataframe_by_name(all_dataframes.get('availability_df')).get_pandas_dataframe()
        specific_order_suborder = self.dataframes_class.get_dataframe_by_name(all_dataframes.get('order_specific_df')).get_pandas_dataframe()
        exec_on_line_df = self.dataframes_class.get_dataframe_by_name(all_dataframes.get('line_indicator')).get_pandas_dataframe()
        penalty_df = self.dataframes_class.get_dataframe_by_name(all_dataframes.get('penalty_df')).get_pandas_dataframe()
        
        # Create sets
        self.m.set_order_suborder = pyo.Set(initialize=order_suborder)
        self.m.set_time = pyo.Set(initialize=time)
        self.m.set_employee_line = pyo.Set(initialize=employee_line)
        self.m.set_employee = pyo.Set(initialize=employee)
        self.m.set_line = pyo.Set(initialize=line)
        
        self.m.set_alloc_index = pyo.Set(initialize=self.m.set_order_suborder * self.m.set_time * self.m.set_employee_line)
    
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
                Expression: 0<= sum over order_suborder's for allocation <= 1
            """
            return (
                0, 
                sum(m.var_alloc[(i, j, k)]
                    for i in m.set_order_suborder
                ),
                1
            )
        #self.m.constr_oneAllocPerEmpl_linPerMoment = pyo.Constraint(self.m.set_time, self.m.set_employee_line, rule=rule_oneAllocPerEmpl_linePerMoment)


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
        #self.m.constr_onlyAllocIfEmpl_lineSkilled = pyo.Constraint(self.m.set_order_suborder, self.m.set_time, self.m.set_employee_line, rule= rule_onlyAllocIfEmpl_lineSkilled)
    

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
        #self.m.constr_onlyAllocIfEmpl_lineAvailable = pyo.Constraint(self.m.set_order_suborder, self.m.set_time, self.m.set_employee_line, rule= rule_onlyAllocIfEmpl_lineAvailable)
    

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
            suborder = specific_order_suborder.loc[i].iloc[1]
            prev_suborder_index = suborder.index(suborder) - 1

            sum_suborders = 0
            for subord in suborder_set:
                if suborder_set.index(subord) == prev_suborder_index:
                    sum_suborder += 1
            
            ratio_completedHours_prevSuborders = sum(
                m.var_alloc[(ord_subord_i, ti_i, empl_line_i)]/time_req_lb.loc[ord_subord_i] 
                for ord_subord_i in m.set_order_suborder 
                for ti_i in m.set_time 
                for empl_line_i in m.set_employee_line
            ) #TODO possibly something wrong with the division. See old code.

            if sum_suborders != 0:
                value = ratio_completedHours_prevSuborders / sum_suborders
            else:
                value = ratio_completedHours_prevSuborders
            
            completed_before = pyo.Var(within=pyo.Binary)
            #FIXME: PrevPercentage: Add the percentage of previous orders that need to be completed.
            #FIXME: Build a construction such that there is a binairy variable, which is equal to one if enough is completed, this can be done by using constraints which make it indicate that.
            return (0, m.var_alloc[i,j,k], 1) if value >= 1 else (0, m.var_alloc[i,j,k], 0)
        #self.m.constr_prevSuborderCompletedBeforeNext = pyo.Constraint(self.m.set_order_suborder, self.m.set_time, self.m.set_employee_line, rule=rule_prevSuborderCompletedBeforeNext)

    
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
        #self.m.constr_lineOrdersOnLine = pyo.Constraint(self.m.set_order_suborder, self.m.set_time, self.m.set_employee, rule=rule_lineOrdersOnLine)


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
            if exec_on_line_df.loc[i].iloc[0]:
                return (0, m.var_alloc[(i, j, k)], 0)
            else:
                return pyo.Constraint.Skip
        #self.m.constr_manualOrdersForEmployee = pyo.Constraint(self.m.set_order_suborder, self.m.set_time, self.m.set_line, rule=rule_manualOrdersForEmployee)


    def solve(self, solver_options=None):
        # Create a solver instance
        solver = pyo.SolverFactory('cbc')

        # Set solver options if provided
        if solver_options:
            for option, value in solver_options.items():
                solver.options[option] = value

        # Solve the model
        results = solver.solve(self.m)

        # Print solver status and results
        #self.m.display()
        print(results)

        # 1. Extract solution values from Pyomo variable
        solution_values = {(i, j, k): self.m.var_alloc[i, j, k].value for (i, j, k) in self.m.set_alloc_index}

        # 2. Create lists of index values for each index set
        index_values = [idx for idx in self.m.set_alloc_index]
        index_names = ['order_suborder', 'time', 'empl_line']
        column_names = ['order_suborder']

        # 3. Create a DataFrame using pandas
        optimal_df = pd.Series(solution_values.values(), index=pd.MultiIndex.from_tuples(index_values, names=index_names))

        optimal_df = optimal_df.unstack(column_names)
        print(optimal_df.copy()[(optimal_df!=0).any(axis=1)])
        # Return the results object
        return results

