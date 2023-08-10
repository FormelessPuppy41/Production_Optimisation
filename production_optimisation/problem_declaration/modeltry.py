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

        # total planned hours per order rule
        
        # Create objective


        # Create Constraints
        def rule_requiredPlannedHours(m, i):
            """Makes sure all orders meet their required amount of planned hours, that is it's lower and upperbound 
            
            Note: The sum in the restriction gives the total amound of planned hours per order.

            Args:
                m (Pyomo Model): Model
                i (str): Order index

            Returns:
                Expression: Used in pyo.Constraint as rule. 
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
            return (
                0, 
                sum(m.var_alloc[(i, j, k)]
                    for i in m.set_order_suborder
                ),
                1
            )
        self.m.constr_oneAllocPerEmpl_linPerMoment = pyo.Constraint(self.m.set_time, self.m.set_employee_line, rule=rule_oneAllocPerEmpl_linePerMoment)

        def rule_onlyAllocIfEmpl_lineSkilled(m, i, j, k):
            suborder = specific_order_suborder.loc[i].iloc[1]
            return (0, 
                    m.var_alloc[(i, j, k)], 
                    skills_df.loc[k, suborder]) #FIXME: During cleaning every none value should be changed to a 0 value. 
        self.m.constr_onlyAllocIfEmpl_lineSkilled = pyo.Constraint(self.m.set_order_suborder, self.m.set_time, self.m.set_employee_line, rule= rule_onlyAllocIfEmpl_lineSkilled)
    
        def rule_onlyAllocIfEmpl_lineAvailable(m, i, j, k):
            return (0, 
                    m.var_alloc[(i, j, k)], 
                    availability_df.loc[j, k]) #FIXME: During cleaning every none value should be changed to a 0 value. 
        self.m.constr_onlyAllocIfEmpl_lineAvailable = pyo.Constraint(self.m.set_order_suborder, self.m.set_time, self.m.set_employee_line, rule= rule_onlyAllocIfEmpl_lineAvailable)
    


    def solve(self):
        solver = pyomo.opt.SolverFactory('cbc')
        results = solver.solve(self.m, tee=True, keepfiles=False, options_string="mip_tolerances_integrality=1e-9 mip_tolerances_mipgap=0")

        if (results.solver.status != pyomo.opt.SolverStatus.ok):
            logging.warning('Check solver not ok?')
        if (results.solver.termination_condition != pyomo.opt.TerminationCondition.optimal):  
            logging.warning('Check solver optimality?') 
        
        print(results)

