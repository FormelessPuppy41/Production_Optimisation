import pandas as pd
from icecream import ic

from typing import Union

from data import ManagerDataframes, OrderDataframe

def main(): 
    managerDF = ManagerDataframes()
    managerDF.process_data()

    """
    for name, config in dfs.items():
        excelFile = config.excelFile
        sheet_name = config.name_excel_sheet
        
        class_name = config.class_type

        bool_read_sheet = config.read_sheet
        read_fillna_value = config.read_fillna_value

        bool_build_df = config.build_df

        #ic(name)

        df_instance: type[BaseDataframe] = class_name(
            _pandas_ExcelFile=excelFile,
            _name_Dataframe=name,
            _name_ExcelSheet=sheet_name,

            _bool_read_df=bool_read_sheet,
            _read_fillna_value = read_fillna_value
        )
        
        df_instance.read_Dataframe_fromExcel()
        
        df_instance.clean()

        if bool_build_df:
            df_instance.build(managerDF=managerDF)

        #ic(df_instance.pandas_Dataframe)
        
        if name == 'BaseDF':
            df_instance.status_cleaned = True
            
        managerDF.store_Dataframe(df_instance)
    """
    
    # Perform some checks with using retrieving methods from dataframes. If those work, then continue to implementing build() for different df's.
    orderDF = managerDF.get_Dataframe('OrderDF', expected_return_type_input=OrderDataframe)
    #ic(orderDF.pandas_Dataframe)
    ic(orderDF.specific_suborder)

    penaltyDF = managerDF.get_Dataframe('PenaltyDF')
    ic(penaltyDF.pandas_Dataframe)

if __name__ == '__main__':
    main()