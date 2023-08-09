import pulp

class Optimization_Model:
    def __init__(self, model_name: str, model_sense: pulp.LpMinimize or pulp.LpMaximize):
        self.model_name = model_name

        self.problem = pulp.LpProblem(name=self.model_name, sense=model_sense)
        self.variables = []
        self.constraints = []

    
    def add_variable(self, variable: pulp.LpVariable):
        self.variables.append(variable)
        self.problem += variable


    def add_constraint(self, constraint: pulp.LpConstraint):
        self.constraints.append(constraint)
        self.problem += constraint

    
    def solve(self):
        self.problem.solve()