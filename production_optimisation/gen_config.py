from __future__ import annotations

from typing import Dict, Type, Union, ForwardRef
from dataclasses import dataclass

import pandas as pd

from data.data import (
    BaseDataframe, 
    OrderDataframe, 
    IndexSetsDataframe, 
    OldPlanningDataframe, 
    ManualPlanningDataframe, 
    AvailabilityDataframe, 
    SkillDataframe, 
    ManagerDataframes, 
    CombinedPlanningDataframe,
    PenaltyDataframe, 
    SolutionDataframe
    )

time_limit = 60
old_planning_limit = '21-08-2023 14:00:00' # Until which point should the old planning be used. Also, format is important, see the format in the oldplanning constraint.


@dataclass
class ConfigBaseDataframe:
    """Class used to present a configuring for BaseDataframes.
    """
    excelFile: pd.ExcelFile = None
    name_excel_sheet: str = None
    class_type: type[BaseDataframe] = BaseDataframe

    read_sheet: bool = True
    read_fillna_value: Union[None, any] = None
    
    build_df: bool = False

@dataclass
class ConfigOrderBased:
    """Class used to present a configuration for properties in the OrderDF. 
    \n That is, which columns to keep in order to get a series of (a single) column(s).
    """
    keepCols: Union[list[str], str]


# Forward declarations for class types
BaseDataframeType = ForwardRef("BaseDataframe")
OrderDataframeType = ForwardRef("OrderDataframe")
IndexSetsDataframeType = ForwardRef("IndexSetsDataframe")
OldPlanningDataframeType = ForwardRef("OldPlanningDataframe")
ManualPlanningDataframeType = ForwardRef("ManualPlanningDataframe")
AvailabilityDataframeType = ForwardRef("AvailabilityDataframe")
SkillDataframeType = ForwardRef("SkillDataframe")
CombinedPlanningDataframeType = ForwardRef("CombinedPlanningDataframe")
PenaltyDataframeType = ForwardRef("PenaltyDataframe")
SolutionDataframeType = ForwardRef("SolutionDataframe")

excelFileRead = pd.ExcelFile(
    "/Users/gebruiker/Documents/GitHub/Production_Optimisation/production_optimisation/EW_Optimisation.xlsm", 
    engine='openpyxl'
    )
excelFileSolution = pd.ExcelFile(
    "/Users/gebruiker/Documents/GitHub/Production_Optimisation/production_optimisation/EW_Optimisation.xlsm", 
    engine='openpyxl'
    )

dfs = {
    # >>>> Name of Dataframe instance: ConfigBaseDataframe[...]
    'BaseDF': ConfigBaseDataframe(
        excelFile=excelFileRead,
        class_type=BaseDataframe,
        read_sheet=False
        ), 
    'OrderDF': ConfigBaseDataframe(
        excelFile=excelFileRead,
        name_excel_sheet='Orders_dataframe',
        class_type=OrderDataframe,
        read_fillna_value=''
        ), 
    'IndexDF': ConfigBaseDataframe(
        excelFile=excelFileRead,
        name_excel_sheet='Index_sets_dataframe', 
        class_type=IndexSetsDataframe,
        read_fillna_value=''
        ),
    'OldPlanningDF': ConfigBaseDataframe(
        excelFile=excelFileRead,
        name_excel_sheet='Planning', 
        class_type=OldPlanningDataframe,
        read_fillna_value=0.0
        ), 
    'ManualPlanningDF': ConfigBaseDataframe(
        excelFile=excelFileRead,
        name_excel_sheet='Manual_planning', 
        class_type=ManualPlanningDataframe,
        read_fillna_value=0.0
        ), 
    'AvailabilityDF': ConfigBaseDataframe(
        excelFile=excelFileRead,
        name_excel_sheet='Config_availability',
        class_type=AvailabilityDataframe,
        read_fillna_value=0.0
        ),
    'SkillDF': ConfigBaseDataframe(
        excelFile=excelFileRead,
        name_excel_sheet='Config_skills', 
        class_type=SkillDataframe,
        read_fillna_value=0.0
        ), 
    'CombinedPlanningDF': ConfigBaseDataframe(
        excelFile=excelFileRead,
        class_type=CombinedPlanningDataframe,
        read_sheet=False,
        build_df=True
        ), 
    'PenaltyDF': ConfigBaseDataframe(
        excelFile=excelFileRead,
        class_type=PenaltyDataframe,
        read_sheet=False,
        build_df=True
        ),
    'SolutionDF': ConfigBaseDataframe(
        excelFile=excelFileSolution,
        name_excel_sheet='Planning',
        class_type=SolutionDataframe,
        read_sheet=False
        )
}

orderBased = {
    # Order/Suborder
    # Specific Components
    'specific_order': ConfigOrderBased(
        keepCols=['Order_number']
    ),
    'specific_suborder': ConfigOrderBased(
        keepCols=['Sub_order']
    ),
    'specific_order_suborder': ConfigOrderBased(
        keepCols=['Order_number', 'Sub_order']
    ), 

    # Next/previous suborder
    'next_suborder': ConfigOrderBased(
        keepCols=['Next_sub_order']
    ),
    'prev_suborder': ConfigOrderBased(
        keepCols=['Previous_sub_order']
    ),

    # Requirements of completion
    'prev_completed_percentage': ConfigOrderBased(
        keepCols=['Percentage_prev_sub_order_needed_before_next_sub_order']
    ), 

    # Date/Time requirements
    # Required time
    'time_req_lowerbound': ConfigOrderBased(
        keepCols=['Time_hours_lowerbound']
    ), 
    'time_req_upperbound': ConfigOrderBased(
        keepCols=['Time_hours_upperbound']
    ),
    # Required dates
    'dates_start': ConfigOrderBased(
        keepCols=['Date_start']
    ), 
    'dates_deadline': ConfigOrderBased(
        keepCols=['Date_deadline']
    ), 

    # Specific order information
    # Executed on line
    'executed_on_line': ConfigOrderBased(
        keepCols=['On_line']
    ),
    # Required line
    'specific_line': ConfigOrderBased(
        keepCols=['Production_line_specific_line']
    ), 
    # Revenue
    'revenue': ConfigOrderBased(
        keepCols=['Revenue']
    ), 
    # Description
    'description': ConfigOrderBased(
        keepCols=['Description']
    ),
    #Manual Urgency
    'manual_urgency': ConfigOrderBased(
        keepCols=['Manual_urgency']
    )
}

# Update forward declarations with actual class types
BaseDataframeType.__forward_arg__ = BaseDataframe
OrderDataframeType.__forward_arg__ = OrderDataframe
IndexSetsDataframeType.__forward_arg__ = IndexSetsDataframe
OldPlanningDataframeType.__forward_arg__ = OldPlanningDataframe
ManualPlanningDataframeType.__forward_arg__ = ManualPlanningDataframe
AvailabilityDataframeType.__forward_arg__ = AvailabilityDataframe
SkillDataframeType.__forward_arg__ = SkillDataframe
CombinedPlanningDataframeType.__forward_arg__ = CombinedPlanningDataframe
PenaltyDataframeType.__forward_arg__ = PenaltyDataframe
SolutionDataframeType.__forward_arg__ = SolutionDataframe
