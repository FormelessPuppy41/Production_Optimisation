import pandas as pd
from icecream import ic

from data import (
    BaseDataframe, 
    ManagerDataframes
    )

def main():
    excelFile = pd.ExcelFile(
        "/Users/gebruiker/Documents/GitHub/Production_Optimisation/production_optimisation/EW_Optimisation.xlsm", 
        engine='openpyxl'
        )

    baseDF = BaseDataframe(
        pandas_ExcelFile=excelFile, 
        name_Dataframe='test_BaseDataframe', 
        name_ExcelSheet='Orders_dataframe'
        )
    
    manager = ManagerDataframes()

    baseDF.read_Dataframe_fromExcel()

    manager.store_Dataframe(
        name_dataframe='orders', 
        dataframe_to_store=baseDF
    )

    ic(baseDF.pandas_Dataframe)

if __name__ == '__main__':
    main()