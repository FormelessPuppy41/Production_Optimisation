import pulp

from general_configuration import data_indexes_columns
from problem_declaration.optimization_model import Optimization_Model
from data.data_process import Data_process

class Variables(Optimization_Model):
    def __init__(self, data_process: Data_process, var_name: str, lowbound: any | None = None, upperbound: float = None, 
                        cat: str = pulp.const.LpContinuous, e: any | None = None):
        super().__init__()
        self.name = var_name
        self.lowbound = None
        self.upperbound = None
        self.catagory = None
        self.equation = None
        self.data_process = None
        self.variable = None

        # Index sets: #FIXME: indexes: Add different (sub)sets such as the unique order code and the emplo_line set and the old and manual ord time sets.
        self.order_index = super().order_index
        self.suborder_index = super().suborder_index
        self.time_index = super().time_index
        self.employee_index = super().employee_index
        self.lines_index = super().lines_index

        self.indexes = {}


    def create_variable(self):
        variable = pulp.LpVariable(name=self.name, lowBound=self.lowbound, upBound=self.upperbound, cat=self.catagory, e=self.equation)
        super().add_variable(variable)
        
    
    def add_index(self, order: bool, suborder: bool, time: bool, employee: bool, line: bool):
        if len(self.indexes) == 0:
            raise print(f'The indices are already added: {self.indexes}')
        if order:
            self.indexes['order'] = self.order_index
        if suborder:
            self.indexes['suborder'] = self.suborder_index
        if time:
            self.indexes['time'] = self.time_index
        if employee:
            self.indexes['employee'] = self.employee_index
        if line:
            self.indexes['line'] = self.lines_index
            

    
    def change_lowbound(self, new_lowbound: float | None = None):
        self.lowbound = new_lowbound

    
    def change_uppbound(self, new_upperbound: float | None = None):
        self.upperbound = new_upperbound

    
    def change_category(self, new_cat: any | None = None):
        if new_cat not in [pulp.LpInteger, pulp.LpContinuous, pulp.LpBinary, None]:
            raise TypeError(f'{new_cat} is not in a category for variables in pulp')
        else:
            self.catagory = new_cat
