import pandas as pd
from icecream import ic

from typing import Union

from data.data import ManagerDataframes, OrderDataframe
from problem_declaration.models_copy import EWOptimisation


def main(): 
    managerDF = ManagerDataframes()
    managerDF.process_data()

    # Perform some checks with using retrieving methods from dataframes. If those work, then continue to implementing build() for different df's.
    orderDF = managerDF.get_Dataframe('OrderDF', expected_return_type_input=OrderDataframe)
    #ic(orderDF.pandas_Dataframe)
    #ic(orderDF.specific_suborder)

    penaltyDF = managerDF.get_Dataframe('PenaltyDF')
    #ic(penaltyDF.pandas_Dataframe)

    model = EWOptimisation(managerDF=managerDF)
    results = model.solve()
    #FIXME: Check all other fixmes
    # Remove branch and remove unnessassary files.
    # relocate this to main.py

    #!!!! Geld zaken regelen voordat ik naar rotterdam ga !!!!!#

if __name__ == '__main__':
    main()