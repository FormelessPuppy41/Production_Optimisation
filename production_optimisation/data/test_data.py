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
    ManagerDataframes, 
    CombinedPlanningDataframe
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
        'BaseDF': [
            None, 
            BaseDataframe,
            False,
            False,
            None
            ], 
        'OrderDF': [
            'Orders_dataframe', 
            OrderDataframe,
            True,
            False,
            ''
            ], 
        'IndexDF': [
            'Index_sets_dataframe', 
            IndexSetsDataframe,
            True,
            False,
            ''
            ],
        'OldPlanningDF': [
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
            ], 
        'AvailabilityDF': [
            'Config_availability',
            AvailabilityDataframe,
            True,
            False,
            0.0
            ],
        'SkillDF': [
            'Config_skills', 
            SkillDataframe,
            True,
            False,
            0.0
            ], 
        'CombinedPlanningDF': [
            None,
            CombinedPlanningDataframe,
            False,
            True,
            None,
            ]
    }        
    # dfs_to_build_columnBased -> based on ordersDF, make subclass of basedataframe: 'orderssubclass ofz' and then for all in 'dfs_to_build_columnBased' a subclass of that classs.
    excelFile = pd.ExcelFile(
        "/Users/gebruiker/Documents/GitHub/Production_Optimisation/production_optimisation/EW_Optimisation.xlsm", 
        engine='openpyxl'
        )

    managerDF = ManagerDataframes()

    for name, config in dfs.items():
        sheet_name, class_name, bool_read_df, bool_build_df, fillna_value = config
        
        ic(name)

        df_instance: BaseDataframe = class_name(
            pandas_ExcelFile =excelFile,
            name_Dataframe=name,
            name_ExcelSheet=sheet_name,
            bool_read_df=bool_read_df,
            fillna_value = fillna_value
        )
        
        df_instance.read_Dataframe_fromExcel()
        
        df_instance.clean()
        if bool_build_df:
            df_instance.build(managerDF=managerDF)
        
        ic(df_instance.pandas_Dataframe)
        
        managerDF.store_Dataframe(df_instance)

    # Perform some checks with using retrieving methods from dataframes. If those work, then continue to implementing build() for different df's.
    df = managerDF.get_Dataframe('BaseDF')
    ic(df.bool_read_df)

if __name__ == '__main__':
    main()