import pyomo
import pyomo.opt
import pyomo.environ as pyo
import pandas
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
            suborder = specific_order_suborder.loc[i].iloc[1]
            prev_suborder_index = suborder.index(suborder) - 1

            sum_suborders = 0
            for subord in suborder_set:
                if suborder_set.index(subord) == prev_suborder_index:
                    sum_suborder += 1
            
            ratio_completedHours_prevSuborders = sum(
                m.var_alloc[(ord_subord_i, ti_i, empl_line_i)]/time_req_lb.loc[ord_subord_i] #FIXME: PrevPercentage: Add the percentage of previous orders that need to be completed.
                for ord_subord_i in m.set_order_suborder 
                for ti_i in m.set_time 
                for empl_line_i in m.set_employee_line
            ) #TODO possibly something wrong with the division. See old code.

            if sum_suborders != 0:
                value = ratio_completedHours_prevSuborders / sum_suborders
            else:
                value = ratio_completedHours_prevSuborders

            return (0, m.var_alloc[i,j,k], value)
        self.m.constr_prevSuborderCompletedBeforeNext = pyo.Constraint(self.m.set_order_suborder, self.m.set_time, self.m.set_employee_line, rule=rule_prevSuborderCompletedBeforeNext)

    def solve(self):
        solver = pyomo.opt.SolverFactory('cbc')
        results = solver.solve(self.m, tee=True, keepfiles=False, options_string="mip_tolerances_integrality=1e-9 mip_tolerances_mipgap=0")

        if (results.solver.status != pyomo.opt.SolverStatus.ok):
            logging.warning('Check solver not ok?')
        if (results.solver.termination_condition != pyomo.opt.TerminationCondition.optimal):  
            logging.warning('Check solver optimality?') 
        
        print(results)

