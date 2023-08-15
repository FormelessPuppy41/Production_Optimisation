import pulp

from data.data_process import Data_process
from problem_declaration.modeltry import EWOptimisation
from problem_declaration.optimization_model import Optimization_Model

import pandas as pd

#FIXME: Ask someone how to properly structure a package, such that relative imports work: what to put in __init__.py files.


process = Data_process('helper_read_dfs')
process.process_helper_read_sheets('EW_initial')
process.process_read_dataframes('EW_read')
process.process_build_dataframes()

ewOpt = EWOptimisation(process.dataframes)
ewOpt.createModel()
ewOpt.solve(solver_options={'timelimit': 60})
# Optimization_Model('EW_min', pulp.LpMinimize)

# write tests that check whether feasability is even possible
# Check combinations of order_suborder on a line, and whether lines can preform this suborder.
# Check whether there is enough timespan to plan all orders. That is per suborder, because if only lines work, then only lines suborders can be scheduled.

# ADD: manual urgency in penalty.

# Seperate the constraints into a class, and make functions that apply individual constraints, where multiple functions can be in one
