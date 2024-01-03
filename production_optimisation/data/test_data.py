import pandas as pd
from icecream import ic

from typing import Union

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

from dataclasses import dataclass

@dataclass
class ConfigBaseDataframe:
    """Class used to present a configuring for BaseDataframes.
    """
    name_excel_sheet: str = None
    class_type: type[BaseDataframe] = BaseDataframe

    read_sheet: bool = True
    read_fillna_value: Union[None, any] = None
    
    build_df: bool = False
    build_column_based: bool = False
    build_indicator_based: bool = False
    build_keep_columns: Union[str, list[str]] = None

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
        'BaseDF': ConfigBaseDataframe(
            class_type=BaseDataframe,
            read_sheet=False
            ), 
        'OrderDF': ConfigBaseDataframe(
            name_excel_sheet='Orders_dataframe',
            class_type=OrderDataframe,
            read_fillna_value=''
            ), 
        'IndexDF': ConfigBaseDataframe(
            name_excel_sheet='Index_sets_dataframe', 
            class_type=IndexSetsDataframe,
            read_fillna_value=''
            ),
        'OldPlanningDF': ConfigBaseDataframe(
            name_excel_sheet='Planning', 
            class_type=OldPlanningDataframe,
            read_fillna_value=0.0
            ), 
        'ManualPlanningDF': ConfigBaseDataframe(
            name_excel_sheet='Manual_planning', 
            class_type=ManualPlanningDataframe,
            read_fillna_value=0.0
            ), 
        'AvailabilityDF': ConfigBaseDataframe(
            name_excel_sheet='Config_availability',
            class_type=AvailabilityDataframe,
            read_fillna_value=0.0
            ),
        'SkillDF': ConfigBaseDataframe(
            name_excel_sheet='Config_skills', 
            class_type=SkillDataframe,
            read_fillna_value=0.0
            ), 
        'CombinedPlanningDF': ConfigBaseDataframe(
            class_type=CombinedPlanningDataframe,
            read_sheet=False,
            build_df=True
            ),
        '': ConfigBaseDataframe(

            )
    }        
    #FIXME: dfs_to_build_columnBased -> based on ordersDF, make subclass of basedataframe: 'orderssubclass ofz' and then for all in 'dfs_to_build_columnBased' a subclass of that classs.
    
    excelFile = pd.ExcelFile(
        "/Users/gebruiker/Documents/GitHub/Production_Optimisation/production_optimisation/EW_Optimisation.xlsm", 
        engine='openpyxl'
        )

    managerDF = ManagerDataframes()

    for name, config in dfs.items():
        sheet_name = config.name_excel_sheet
        class_name = config.class_type
        bool_read_df = config.read_sheet
        bool_build_df = config.build_df
        fillna_value = config.read_fillna_value

        ic(name)

        df_instance: type[BaseDataframe] = class_name(
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
        
        if name == 'BaseDF':
            df_instance.status_cleaned = True
            
        managerDF.store_Dataframe(df_instance)

    # Perform some checks with using retrieving methods from dataframes. If those work, then continue to implementing build() for different df's.
    df = managerDF.get_Dataframe('BaseDF')
    ic(df.bool_read_df)

if __name__ == '__main__':
    main()