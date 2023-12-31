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
#TODO: Add main() in parts to data.py
# dfs in beginning file or import from gen.config
# functionalities partitioned in different classes, either manager or new class for processing data which returns a manager. probably new class.
def main(): 

    dfs = {
        # >>>> Name of instance: [
        # >>>>      name of excelSheet: str
        # >>>>      Class type of Dataframe: BaseDataframe // Subclass
        # >>>>      Read Sheet: bool
        # >>>>      Build DF: bool #FIXME: Is this necessary, since each build is defined for each class already.
        # >>>>      Read Fillna_Value: any #FIXME: Could fillna_value be removed from all constructors, and replaced with a chance method if it is needed for a df?
        # >>>> ],
        'baseDF': [
            None, 
            BaseDataframe,
            False,
            False,
            None
            ], 
        'orderDF': [
            'Orders_dataframe', 
            OrderDataframe,
            True,
            False,
            ''
            ], 
        'indexDF': [
            'Index_sets_dataframe', 
            IndexSetsDataframe,
            True,
            False,
            ''
            ],
        'oldPlanningDF': [
            'Planning', 
            OldPlanningDataframe,
            True,
            False,
            0.0
            ], 
        'ManualPlanningDF': [
            'Manual_planning', 
            ManualPlanningDataframe,
            True,
            False,
            0.0
            ]
    }        

    excelFile = pd.ExcelFile(
        "/Users/gebruiker/Documents/GitHub/Production_Optimisation/production_optimisation/EW_Optimisation.xlsm", 
        engine='openpyxl'
        )

    dfManager = ManagerDataframes()

    for name, config in dfs.items():
        sheet_name, class_name, bool_read_df, bool_build_df, fillna_value = config
        
        df_instance: BaseDataframe = class_name(
            pandas_ExcelFile =excelFile,
            name_Dataframe=name,
            name_ExcelSheet=sheet_name,
            bool_read_df=bool_read_df,
            fillna_value = fillna_value
        )
        
        df_instance.read_Dataframe_fromExcel()
        
        df_instance.clean()
        
        ic(df_instance.pandas_Dataframe)
        
        dfManager.store_Dataframe(df_instance)

    # Perform some checks with using retrieving methods from dataframes. If those work, then continue to implementing build() for different df's.
    df = dfManager.get_Dataframe('baseDF')
    ic(df.bool_read_df)

if __name__ == '__main__':
    main()