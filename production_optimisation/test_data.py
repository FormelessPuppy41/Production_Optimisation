import pandas as pd
from icecream import ic

from typing import Union

from data.data import ManagerDataframes, OrderDataframe


def main(): 
    managerDF = ManagerDataframes()
    managerDF.process_data()

    # Perform some checks with using retrieving methods from dataframes. If those work, then continue to implementing build() for different df's.
    orderDF = managerDF.get_Dataframe('OrderDF', expected_return_type_input=OrderDataframe)
    ic(orderDF.pandas_Dataframe)
    #ic(orderDF.specific_suborder)

    penaltyDF = managerDF.get_Dataframe('PenaltyDF')
    ic(penaltyDF.pandas_Dataframe)

    #FIXME: Check all other fixmes
    # Add models.

if __name__ == '__main__':
    main()