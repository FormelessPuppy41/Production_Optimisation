import pulp

from data.data_process import Data_process
from problem_declaration.optimization_model import Optimization_Model

import pandas as pd

#FIXME: Ask someone how to properly structure a package, such that relative imports work: what to put in __init__.py files.


process = Data_process('helper_read_dfs')
process.process_helper_read_sheets('EW_initial')
process.process_read_dataframes('EW_read')
process.process_build_dataframes()


# Optimization_Model('EW_min', pulp.LpMinimize)

