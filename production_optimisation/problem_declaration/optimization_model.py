import pulp

from general_configuration import data_indexes_columns
from data.data_process import Data_process

class Optimization_Model:
    def __init__(self, data_process: Data_process):
        self.data_process = data_process

        self.problem: pulp.LpProblem
        self.variables = []
        self.constraints = []

        # Indexsets
        self.order_index = self.data_process.process_get_index(data_indexes_columns.get('orders'))
        self.suborder_index = self.data_process.process_get_index(data_indexes_columns.get('suborders'))
        self.time_index = self.data_process.process_get_index(data_indexes_columns.get('time'))
        self.employee_index = self.data_process.process_get_index(data_indexes_columns.get('employees'))
        self.lines_index = self.data_process.process_get_index(data_indexes_columns.get('lines'))


    def create_problem(self, prob_name: str):
        return pulp.LpProblem(prob_name, self.model_sense)
    

    def add_variable(self, variable: pulp.LpVariable):
        self.variables.append(variable)
        self.problem += variable


    def add_constraint(self, constraint: pulp.LpConstraint):
        self.constraints.append(constraint)
        self.problem += constraint

    
    def solve(self):
        self.problem.solve()


    def add_model_sense(self, model_sense: pulp.LpMinimize or pulp.LpMaximize):
        self.model_sense = model_sense
    
