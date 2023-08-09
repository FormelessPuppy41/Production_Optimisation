import pulp

class Variable:
    def __init__(self, var_name: str, lowbound: any | None = None, upperbound: float = None, 
                        cat: str = pulp.const.LpContinuous, e: any | None = None):
        self.name = var_name
        self.variable = pulp.LpVariable(name=var_name, lowBound=lowbound, upBound=upperbound, cat=cat, e=e)

    def create_variable(self, var_name: str, lowbound: any | None = None, upperbound: float = None, 
                        cat: str = pulp.const.LpContinuous, e: any | None = None):
        variable = pulp.LpVariable(name=var_name, lowBound=lowbound, upBound=upperbound, cat=cat, e=e)
        return variable
    

