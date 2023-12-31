import pandas as pd
from icecream import ic

from data import (
    BaseDataframe, 
    OrderDataframe, 
    IndexSetsDataframe, 
    OldPlanningDataframe, 
    ManualPlanningDataframe, 
    AvailabilityDataframe, 
    SkillDataframe, 
    ManagerDataframes
    )

def main():

    dfs = {
        # >>>> Name of instance: [
        # >>>>      name of excelSheet: str
        # >>>>      Class type of Dataframe: BaseDataframe // Subclass
        # >>>>      Read Sheet: bool
        # >>>>      Build DF: bool #FIXME: Is this necessary, since each build is defined for each class already.
        # >>>> ],
        'baseDF': [
            None, 
            BaseDataframe,
            False,
            False
            ], 
        'orderDF': [
            'Orders_dataframe', 
            OrderDataframe,
            True,
            False
            ], 
        'indexDF': [
            'Index_sets_dataframe', 
            IndexSetsDataframe,
            True,
            False
            ],
        'oldPlanningDF': [
            'Planning', 
            OldPlanningDataframe,
            True,
            False
            ], 
        'ManualPlanningDF': [
            'Manual_planning', 
            ManualPlanningDataframe,
            True,
            False
            ]
    }        

    excelFile = pd.ExcelFile(
        "/Users/gebruiker/Documents/GitHub/Production_Optimisation/production_optimisation/EW_Optimisation.xlsm", 
        engine='openpyxl'
        )

    dfManager = ManagerDataframes()

    for name, config in dfs.items():
        sheet_name, class_name, bool_read_df, bool_build_df = config
        df_instance: BaseDataframe = class_name(
            pandas_ExcelFile =excelFile,
            name_Dataframe=name,
            name_ExcelSheet=sheet_name,
            bool_read_df=bool_read_df
        )
        df_instance.read_Dataframe_fromExcel()

        ic(name)
        ic(df_instance.pandas_Dataframe)
        
        df_instance.clean()
        
        ic(df_instance.pandas_Dataframe)
        
        dfManager.store_Dataframe(df_instance)

    df = dfManager.get_Dataframe('baseDF')
    ic(df.bool_read_df)

if __name__ == '__main__':
    main()