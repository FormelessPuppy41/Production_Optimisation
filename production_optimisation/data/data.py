from __future__ import annotations 
# Used in building dataframes, since the ManagerDataframes is located at the end of the file. 
# Subsequent of all DF's that are build and need a ManagerDataframe as input

import pandas as pd
import numpy as np
import openpyxl

from icecream import ic
from typing import Union, TypeVar


class BaseDataframe:
    """The basic methods and attributes for a Dataframe. They are further specified in their own subclass.
    """
    def __init__(
            self, 
            _pandas_ExcelFile: pd.ExcelFile, 
            _name_Dataframe: str, 
            _name_ExcelSheet: str = None,
            _bool_read_df: bool = True,
            _bool_build_df: bool = False, 
            _read_fillna_value = None
            ) -> None:
        
        self._name_Dataframe = _name_Dataframe
        self._name_ExcelSheet = _name_ExcelSheet
        
        self._bool_read_df = _bool_read_df 
        self._bool_build_df = _bool_build_df

        self._pandas_ExcelFile  = _pandas_ExcelFile
        self._pandas_Dataframe: Union[
            pd.DataFrame, 
            pd.Series
            ] = pd.DataFrame()

        self._status_cleaned: bool = False

        if not _read_fillna_value:
            self._read_fillna_value = ''
        else:
            self._read_fillna_value = _read_fillna_value


    ### RETRIEVING INFORMATION ABOUT THE DATAFRAME
    # Retrieve names
            
    ### PROPERTIES AND SETTERS
    @property
    def name_Dataframe(self) -> str:
        return self._name_Dataframe
    @name_Dataframe.setter
    def name_Dataframe(self, new_name_Dataframe: str):
        self._name_Dataframe = new_name_Dataframe

    @property
    def name_ExcelSheet(self) -> str:
        return self._name_ExcelSheet
    @name_ExcelSheet.setter
    def name_ExcelSheet(
            self, 
            name_new_ExcelSheet: str
            ):
        """Changes the name of the excel sheet where the dataframe can be found or should be written to {name_new_ExcelSheet}

        Args:
            name_new_ExcelSheet (str): Name of the new excel_sheet where the dataframe can be found or should be written to.
        """
        self._name_ExcelSheet = name_new_ExcelSheet

    @property
    def pandas_ExcelFile(self) -> pd.ExcelFile:
        return self._pandas_ExcelFile
    @pandas_ExcelFile.setter
    def pandas_ExcelFile(self, new_Pandas_ExcelFile: pd.ExcelFile):
        self._pandas_ExcelFile = new_Pandas_ExcelFile

    @property
    def pandas_Dataframe(self) -> type[pd.DataFrame]:
        return self._pandas_Dataframe
    @pandas_Dataframe.setter
    def pandas_Dataframe(
            self, 
            changed_Dataframe: Union[
                pd.DataFrame, 
                pd.Series
                ]
            ):
        """Changes the pd.DataFrame/pd.Series to {changed_Dataframe}. 

        Args:
            changed_Dataframe (Union[ Type[pd.DataFrame], Type[pd.Series] ]): The pd.DataFrame/Series to change the current _pandas_Dataframe to.
        """
        self._pandas_Dataframe = changed_Dataframe

    @property
    def read_fillna_value(self):
        return self._read_fillna_value
    @read_fillna_value.setter
    def read_fillna_value(
            self, 
            new_value
            ):
        """Changes the value that the NaN values are filled with. 

        Args:
            new_value (_type_): The new value which fills the NaN values.
        """
        if not new_value:
            self._read_fillna_value = ''
        else:
            self._read_fillna_value = new_value

    @property
    def status_cleaned(self) -> bool:
        return self._status_cleaned
    @status_cleaned.setter
    def status_cleaned(
            self, 
            new_status: bool
            ):
        """Changes the cleaned status of the dataframe to {new_status} to indicate whether the dataframe has been cleaned or not.

        Args:
            new_status (bool): True if cleaned, False if not cleaned.
        """
        self._status_cleaned = new_status

    @property
    def bool_read_df(self) -> bool:
        return self._bool_read_df
    @bool_read_df.setter
    def bool_read_df(self, new_bool_read_df: bool):
        self._bool_read_df = new_bool_read_df
    
    @property
    def bool_build_df(self) -> bool:
        return self._bool_build_df
    @bool_build_df.setter
    def bool_build_df(self, new_bool_build_df: bool):
        self._bool_build_df = new_bool_build_df
    
    ### ACTIONS PERFORMED ON THE DATAFRAME
    def clean(self):
        """Empty clean function, since cleaning method depends on the Dataframe type. \n Specify the subclass in order to clean it.
        """
        pass
    
    ### BUILDING FUNCTIONS
    def build(self):
        """Empty build function, since building method depends on the Dataframe type. \n Specify the subclass in order to build it.
        """
        pass
    
    def indicatorBuilder(
                self, 
                managerDF: ManagerDataframes,  
                keepCols: Union[
                    str, 
                    list[str]
                    ]
                ):
            """Get a indicator of the OrderDF where the columns 'keepCols' are kept. And saves the new PandasDF

            Args:
                managerDF (ManagerDataframes): ManagerDataframe that should contain OrderDf, precense is validated within function.
                keepCols (Union[str, list[str]]): columns to keep as indicators. Values within column must be 0/1 or False/True
            """
            # Obtain the ordersDF.
            orderDF = managerDF.get_Dataframe('OrderDF').pandas_Dataframe.copy()
            
            # Get columns to drop.
            drop_cols = [
                col for col in orderDF.columns 
                if col not in keepCols
                ]
            newDF = orderDF.drop(columns=drop_cols)

            # Make Indicator: if value is True or 1 then True, else False.
            newDF = (newDF == True) | (newDF == 1)
            
            self._pandas_Dataframe = newDF
    
    def columnBasedBuilder(
            self, managerDF: 
            ManagerDataframes, 
            keepCols: Union[
                str, 
                list[str]
                ]
            ):
        pass
    
    ### COPYING TO NEW BASEDATAFRAME INSTANCE
    def copy_to_new_Dataframe(
            self, 
            name_new_Dataframe: str
            ):
        """Makes a copy of the current Dataframe and returns a new instance of the Dataframe, with a new name. All other attributes are the same.

        Args:
            name_new_Dataframe (str): name of the new dataframe.

        Returns:
            type(equal to the type of the called on Dataframe // (sub)class of BaseDataframe): The copy instance of the Dataframe.
        """

        # Create the new instance
        new_Dataframe = BaseDataframe(
            self._pandas_ExcelFile, 
            name_new_Dataframe, 
            self._name_ExcelSheet
            )
        
        # Change the pandas dataframe to be the same as the original
        new_Dataframe.pandas_Dataframe = self._pandas_Dataframe
        
        # If the original was already cleaned, then the status of new df should also be True, else it will be False.
        new_Dataframe._status_cleaned = self._status_cleaned
        
        return new_Dataframe

    ### READING/WRITING DATA FROM/TO EXCEL
    def read_Dataframe_fromExcel(self):
        """Read the dataframe from excel, if indicated in df declaration that it is needed (_bool_read_df). 
        \n Validates whether the name of the excelsheet can be found.

        Raises:
            ValueError: Dataframe does not have a value for {_name_ExcelSheet}.
            ValueError: Dataframe's {_name_ExcelSheet} cannot be found in the sheet_names of the ExcelFile.
        """
        if self._bool_read_df:
            self._validate_name_ExcelSheet()
            
            self._pandas_Dataframe = pd.read_excel(
                io=self._pandas_ExcelFile.io,
                sheet_name=self._name_ExcelSheet,
                engine='openpyxl'
            ).fillna(self._read_fillna_value)

    #FIXME: Create VBA file that communicates with python to indicate whether a file is opened by the user, then the dataframe will not be written to excel until the file is closed. otherwise there will be alot of corrupt files.
    def write_Dataframe_toExcel(self):
        """Write the dataframe to excel. 
        \n Validates whether the name of the excelsheet can be found.

        Raises:
            ValueError: Dataframe does not have a value for {_name_ExcelSheet}.
            ValueError: Dataframe's {_name_ExcelSheet} cannot be found in the sheet_names of the ExcelFile.
        """
        self._validate_name_ExcelSheet()

        # Use pd.ExcelWriter as a Writer, to write the excelfile to a sheet in the ExcelFile.
        with pd.ExcelWriter(
            path=self._pandas_ExcelFile.io, 
            mode='a', 
            if_sheet_exists='replace', 
            engine='openpyxl', 
            engine_kwargs={'keep_vba': True}
            ) as writer:

            self._pandas_Dataframe.to_excel(
                excel_writer=writer, 
                sheet_name=self._name_ExcelSheet, 
                index=True
                )
        
        ic(f'Dataframe ({self._name_Dataframe}) written to ExcelFile in sheet ({self._name_ExcelSheet}) correctly.')

    ### DATA VALIDATION.
    #FIXME: Add data validation for missing data. Same for other dataframes that have index sets as input, are they the correct format?
    def validate_data(self):
        pass

    ### HELPER FUNCTIONS
    # Validation
    def _validate_name_ExcelSheet(self):
        """Validate whether the name of the ExcelSheet can be found in the sheet_names of the ExcelFile.

        Raises:
            ValueError: Dataframe does not have a value for {_name_ExcelSheet}.
            ValueError: Dataframe's {_name_ExcelSheet} cannot be found in the sheet_names of the ExcelFile.
        """
        # If there is no excel sheet name
        if self._name_ExcelSheet is None:
            raise ValueError(
                f'Dataframe ({self._name_Dataframe}) does not have its own sheet in the ExcelFile ({self._pandas_ExcelFile})'
                )
        
        # If the given sheet_name cannot be found in the corresponding ExcelFile. 
        elif self._name_ExcelSheet not in self._pandas_ExcelFile.sheet_names:
            raise ValueError(
                f'The given sheetname ({self._name_ExcelSheet}) for the dataframe ({self._name_Dataframe}) cannot be found in the sheet_names within the given ExcelFile ({self._pandas_ExcelFile})'
                )
        
        # If the given sheet_name can be found in the given ExcelFile.
        pass
    
    # Frame manipulations
    def _change_index_to_firstCol(self):
        """Changes the index of the dataframe to the first column of the dataframe.
        """
        if not self._pandas_Dataframe.empty:
            columns = self._pandas_Dataframe.columns
            self._pandas_Dataframe = self._pandas_Dataframe.set_index(columns[0])



class OrderDataframe(BaseDataframe):
    """The ordersDataframe is a class that is used to describe the ordersDF.

    Subclass of:
        BaseDataframe: Basic description of Dataframes.
    """
    def __init__(
            self, 
            _pandas_ExcelFile: pd.ExcelFile, 
            _name_Dataframe: str, 
            _name_ExcelSheet: str = None, 
            _bool_read_df: bool = True, 
            _bool_build_df: bool = False, 
            _read_fillna_value = None
            ) -> None:
        
        super().__init__(
            _pandas_ExcelFile, 
            _name_Dataframe, 
            _name_ExcelSheet, 
            _bool_read_df,
            _bool_build_df, 
            _read_fillna_value
            )

    ### SUBCLASS SPECIFIC FUNCTIONS
    def clean(self):
        """Cleans the orders dataframe by changing all strings to uppercase and otherwise returning the element for the columns that need to be cleaned.

        str -> uppercase
        else -> element
        """
        # Check if the dataframe has not yet been cleaned, if so, clean it.
        if not self._status_cleaned:
            self._change_index_to_firstCol()  

            # During cleaning the description column is excluded to preserve the format.
            columns_to_exclude_cleaning = ['Description']
            columns_to_clean = self._pandas_Dataframe.columns.drop(columns_to_exclude_cleaning)
            
            # Clean individual column elements
            for col in columns_to_clean:
                self._pandas_Dataframe[col] = self._pandas_Dataframe[col].apply(
                        lambda x: self._clean_orderDF_elements(x)
                        )
            
            # Remove empty rows
            self._pandas_Dataframe = self._pandas_Dataframe[self._pandas_Dataframe != '']
            self._pandas_Dataframe.fillna(self._read_fillna_value)
            
            self._status_cleaned = True

    ### HELPER FUNCTIONS
    def _clean_orderDF_elements(self, element):
        """This function cleans the actual elements of each column based on the datatype of the column.
        \n
        String -> uppercase String
        Else -> No change

        Args:
            element (_type_): elements of the ordersDF

        Returns:
            _type_: The cleaned element
        """
        if element:
            if pd.notna(element) and isinstance(element, str):
                return element.upper()
            
            elif pd.notna(element):
                return element
    


class IndexSetsDataframe(BaseDataframe):
    """The indexSetsDataframe is a class that is used to describe the IndexDF.

    Subclass of:
        BaseDataframe: Basic description of Dataframes.
    """
    def __init__(
            self, 
            _pandas_ExcelFile: pd.ExcelFile, 
            _name_Dataframe: str, 
            _name_ExcelSheet: str = None, 
            _bool_read_df: bool = True,
            _bool_build_df: bool = False, 
            _read_fillna_value = None
            ) -> None:
        
        super().__init__(
            _pandas_ExcelFile, 
            _name_Dataframe, 
            _name_ExcelSheet, 
            _bool_read_df,
            _bool_build_df,
            _read_fillna_value
            )
    
    #FIXME: Make this variable, such that they van be changed in the initial configuration instead of here, use a dictionary.
    def __post_cleaning__(self):
        self._orders_suborder = self._remove_values_from_series(
            series=self._pandas_Dataframe['Orders_suborders'], 
            value_to_replace=''
            ).to_list()
        ic(self._orders_suborder)
        self._orders = self._remove_values_from_series(
            series=self._pandas_Dataframe['Orders'], 
            value_to_replace=''
            ).to_list()
        self._suborders = self._remove_values_from_series(
            series=self._pandas_Dataframe['Sub_orders'], 
            value_to_replace=''
            ).to_list()
        self._time_intervals = self._remove_values_from_series(
            series=self._pandas_Dataframe['Time_intervals'], 
            value_to_replace=''
            ).to_list()
        self._employee_line = self._remove_values_from_series(
            series=self._pandas_Dataframe['Employee_line'], 
            value_to_replace=''
            ).to_list()
        self._employees = self._remove_values_from_series(
            series=self._pandas_Dataframe['Employees'], 
            value_to_replace=''
            ).to_list()
        self._lines = self._remove_values_from_series(
            series=self._pandas_Dataframe['Production_lines'], 
            value_to_replace=''
            ).to_list()
   
    ### PROPTERTIES OF INDEX SETS: SPECIFIC INDEX SETS
    @property
    def orders_suborder(self):
        return self._orders_suborder
    
    @property
    def orders(self):
        return self._orders
    
    @property
    def suborders(self):
        return self._suborders
    
    @property
    def time_intervals(self):
        return self._time_intervals
    
    @property
    def employee_line(self):
        return self._employee_line
    
    @property
    def employee(self):
        return self._employees
    
    @property
    def line(self):
        return self._lines
    
    ### CLEAN FUNCTION
    def clean(self):
        """Clean the indexDF by changing all strings to uppercase, timestamp is left as it is, floats are made to integer.

        str -> uppercase
        pd.timestamp -> element
        float -> int
        """
        if not self._status_cleaned:
            for col in self._pandas_Dataframe.columns:
                self._pandas_Dataframe[col] = self._pandas_Dataframe[col].apply(
                    lambda x: self._clean_indexDF_elements(x)
                    )
            
            self.__post_cleaning__()
            self._status_cleaned = True  

    ### HELPER FUNCTIONS
    def _clean_indexDF_elements(self, element):
        """This function cleans all the actual elements based on their datatype
        \n
        str -> uppercase
        pd.Timestamp -> same
        float -> int

        Args:
            element (_type_): elements of the indexDF

        Returns:
            _type_: The cleaned element
        """
        if element:
            if isinstance(element, str):
                return element.upper()
            elif isinstance(element, pd.Timestamp):
                return element
            elif isinstance(element, float):
                return int(element)
        else:
            return element

    def _remove_values_from_series(
            self, 
            series: pd.Series, 
            value_to_replace
            ) -> pd.Series:
        """Removes specific values from a series by replacing them with pd.NA and applying .dropna()

        Args:
            series (pd.Series): Series to drop values from
            value_to_replace (_type_): Values to drop

        Returns:
            pd.Series: Series without the removed values.
        """
        return series.replace(to_replace=value_to_replace, value=pd.NA).dropna()


class OldPlanningDataframe(BaseDataframe):
    """The oldPlanningDataframe is a class that is used to describe the oldPlanningDF.

    Subclass of:
        BaseDataframe: Basic description of Dataframes.
    """
    def __init__(
            self, 
            _pandas_ExcelFile: pd.ExcelFile, 
            _name_Dataframe: str, 
            _name_ExcelSheet: str = None, 
            _bool_read_df: bool = True,
            _bool_build_df: bool = False, 
            _read_fillna_value = None
            ) -> None:
        
        super().__init__(
            _pandas_ExcelFile, 
            _name_Dataframe, 
            _name_ExcelSheet, 
            _bool_read_df,
            _bool_build_df,
            _read_fillna_value
            )

    def clean(self):
        """Clean the oldPlanningDF by changing all strings to uppercase, timestamp is left as it is, floats are made to integer.

        str -> uppercase
        pd.timestamp -> element
        float -> int
        """
        if not self._pandas_Dataframe.empty and not self._status_cleaned:
            columns = self._pandas_Dataframe.columns.to_list()
            index_columns = [idx for idx in columns if columns.index(idx) <= 2]

            self._pandas_Dataframe = self._pandas_Dataframe.set_index(index_columns)
            self._pandas_Dataframe.columns = ['allocation']

            # Change format to pd.Series
            self._pandas_Dataframe = self._pandas_Dataframe.iloc[:, 0]

            # Drop rows with value 0.0
            self._pandas_Dataframe = self._pandas_Dataframe[self._pandas_Dataframe != 0.0]

            self._status_cleaned = True



class ManualPlanningDataframe(BaseDataframe):
    """The oldPlanningDataframe is a class that is used to describe the oldPlanningDF.

    Subclass of:
        BaseDataframe: Basic description of Dataframes.
    """
    def __init__(
            self, 
            _pandas_ExcelFile: pd.ExcelFile, 
            _name_Dataframe: str, 
            _name_ExcelSheet: str = None, 
            _bool_read_df: bool = True,
            _bool_build_df: bool = False, 
            _read_fillna_value = None
            ) -> None:
        
        super().__init__(
            _pandas_ExcelFile, 
            _name_Dataframe, 
            _name_ExcelSheet, 
            _bool_read_df,
            _bool_build_df,
            _read_fillna_value
            )

    def clean(self):
        """Clean the manualPlanningDataframe by changing all strings to uppercase, timestamp is left as it is, floats are made to integer.

        str -> uppercase
        pd.timestamp -> element
        float -> int
        """
        if not self._pandas_Dataframe.empty and not self._status_cleaned:
            # Change index to first two columns. (order_suborder, empl_line)
            index_columns = self._pandas_Dataframe.columns.to_list()[:2]
            self._pandas_Dataframe = self._pandas_Dataframe.set_index(index_columns)
            
            # Rename the datestamp columns to 'time'
            self._pandas_Dataframe = self._pandas_Dataframe.rename_axis('time', axis=1)
            
            # Stack columns to get a pd.Series and rename the index.
            self._pandas_Dataframe = self._pandas_Dataframe.stack()
            self._pandas_Dataframe.name = 'allocation'

            # Reorder the index
            self._pandas_Dataframe = self._pandas_Dataframe.reorder_levels(
                ['order_suborder','time', 'empl_line']
                )

            # Replace Empty values ('') to 0.0
            self._pandas_Dataframe = self._pandas_Dataframe.replace('', 0.0)
            
            # Drop rows with value 0.0
            self._pandas_Dataframe = self._pandas_Dataframe[self._pandas_Dataframe != 0.0]
            
            self._status_cleaned = True



class AvailabilityDataframe(BaseDataframe):
    def __init__(
            self, 
            _pandas_ExcelFile: pd.ExcelFile, 
            _name_Dataframe: str, 
            _name_ExcelSheet: str = None, 
            _bool_read_df: bool = True, 
            _bool_build_df: bool = False, 
            _read_fillna_value = None
            ) -> None:
        super().__init__(
            _pandas_ExcelFile, 
            _name_Dataframe, 
            _name_ExcelSheet, 
            _bool_read_df,
            _bool_build_df,
            _read_fillna_value
            )
    
    def clean(self):
        """Cleans the AvailabilityDataframe, that is change index to the first column.
        """
        if not self._status_cleaned:
            self._change_index_to_firstCol()

            self._status_cleaned = True



class SkillDataframe(BaseDataframe):
    def __init__(
            self, 
            _pandas_ExcelFile: pd.ExcelFile, 
            _name_Dataframe: str, 
            _name_ExcelSheet: str = None, 
            _bool_read_df: bool = True,
            _bool_build_df: bool = False, 
            _read_fillna_value = None
            ) -> None:
        super().__init__(
            _pandas_ExcelFile, 
            _name_Dataframe, 
            _name_ExcelSheet, 
            _bool_read_df,
            _bool_build_df,
            _read_fillna_value
            )
    
    def clean(self):
        """Cleans the skillDataframe, that is change index to the first column.
        """
        if not self._status_cleaned:
            self._change_index_to_firstCol()

            self._status_cleaned = True


### DATAFRAMES THAT ARE BUILD

class CombinedPlanningDataframe(BaseDataframe):
    def __init__(
            self, 
            _pandas_ExcelFile: pd.ExcelFile, 
            _name_Dataframe: str, 
            _name_ExcelSheet: str = None, 
            _bool_read_df: bool = True, 
            _bool_build_df: bool = False, 
            _read_fillna_value=None
            ) -> None:
        super().__init__(
            _pandas_ExcelFile, 
            _name_Dataframe, 
            _name_ExcelSheet, 
            _bool_read_df, 
            _bool_build_df, 
            _read_fillna_value
            )
    
    def clean(self):
        """Does nothing since dataframe is not read and not cleaned, but build using clean dataframes.
        """
        pass

    def build(self, managerDF: ManagerDataframes):
        """Build the pandas dataframe of CombinedPlanningDF, which shows all manually scheduled allocations and the OldPlanning allocations that adhere to the datelimit condition. That condition indicates that only previous allocations are copied if they are before the limit_OldPlanning timestamp.

        Args:
            managerDF (ManagerDataframes): Manager containing the 'OldPlanningDF' and 'ManualPlanningDF', they should be cleaned.
        
        """
        oldPlanningDF, manualPlanningDF = managerDF.get_Dataframe(
            dfs_to_get=['OldPlanningDF', 'ManualPlanningDF']
            )

        combinedPlanningDF: pd.DataFrame = pd.DataFrame()

        ### GET PANDAS DF'S OF INSTANCES
        # Get the oldPlanningDF that satisfies the condition. That is, is allocated before limit_oldPlanning
        oldPlanningDF = self._apply_oldPlanning_condition(oldPlanningDataframe=oldPlanningDF)
        manualPlanningDF = manualPlanningDF.pandas_Dataframe

        ### CONDITIONS FOR COMBINEDPLANNINGDF

        # If both plannings are empty, return empty df.
        if manualPlanningDF.empty and oldPlanningDF.empty:
            return combinedPlanningDF

        elif manualPlanningDF.empty:
            combinedPlanningDF = oldPlanningDF
        
        elif oldPlanningDF.empty:
            combinedPlanningDF = manualPlanningDF

         # If both plannings are not empty, return the concatenated result, including both
        else: 
            index_names_oldDF = oldPlanningDF.index.names
            # Join both dataframes using set theory: (A U B), so in either A or B.
            combinedPlanningDF = pd.concat(
                [manualPlanningDF, oldPlanningDF], 
                join='outer'
                ) 

            # Remove duplicates if combination is in both plannings.
            combinedPlanningDF = combinedPlanningDF.reset_index().drop_duplicates(
                subset=list(index_names_oldDF), 
                keep='first'
                ).set_index(index_names_oldDF) # drop_duplicates is column based, so reset index.
        
        self._pandas_Dataframe = combinedPlanningDF

    # HELPER FUNCTIONS    
    def _apply_oldPlanning_condition(self, oldPlanningDataframe: BaseDataframe) -> pd.DataFrame:
        """Applies the oldPlanning condition, where only allocations before the limit_OldPlanning are considered. 

        Args:
            oldPlanningDF (pd.DataFrame): OldPlanningDF that shows all the previous allocations.

        Returns:
            pd.DataFrame: OldPlanningDF with only allocations satisfying the condition.
        """
        oldPlanningDF = oldPlanningDataframe.pandas_Dataframe

        # Obtain limit_oldPlanning
        limit_OldPlanning = self._get_formatted_limit_OldPlanning()

        if not oldPlanningDF.empty:

            # Reset index for enabling conditioning on 'time' index/column
            index_names_oldDF = oldPlanningDF.index.names
            oldPlanningDF = oldPlanningDF.reset_index() 

            # Only keep old allocations that happen before the 'limit_oldPlanning' value.
            condition_oldDF = (oldPlanningDF['time'] <= pd.to_datetime(limit_OldPlanning))
            
            # Only keep rows that satisfy the condition
            oldPlanningDF = oldPlanningDF[condition_oldDF]
            
            # Reformat to Series with correct index.
            oldPlanningDF = oldPlanningDF.set_index(index_names_oldDF)['allocation']

        return oldPlanningDF
    
    def _get_formatted_limit_OldPlanning(self) -> pd.Timestamp:
        """Get the limit_OldPlanning, that indicates until which point in time the OldPlannigDF is to be followed. 
        Is returned in "%Y-%m-%d %H:%M:%S" format.

        Returns:
            pd.Timestamp: limit_OldPlanning value, that indicates until when OldPlanningDF will be adhered.
        """
        from dateutil import parser

        #TODO: Relocate to new general_Config file. and import here
        # Until which point should the old planning be used. Also, format is important, see the format in the oldplanning constraint.
        limit_oldPlanning = '21-08-2023 14:00:00' 

        # Reformat by parsing into subparts and changing format.
        parsed_datetime = parser.parse(limit_oldPlanning)
        limit_oldPlanning = parsed_datetime.strftime("%Y-%m-%d %H:%M:%S")
        
        return limit_oldPlanning
    


#FIXME: Complete
class PenaltyDataframe(BaseDataframe):
    def __init__(
            self, _pandas_ExcelFile: pd.ExcelFile, 
            _name_Dataframe: str, 
            _name_ExcelSheet: str = None, 
            _bool_read_df: bool = True, 
            _bool_build_df: bool = False, 
            _read_fillna_value=None
            ) -> None:
        super().__init__(
            _pandas_ExcelFile, 
            _name_Dataframe, 
            _name_ExcelSheet, 
            _bool_read_df, 
            _bool_build_df, 
            _read_fillna_value
            )
    
    def build():
        pass
    


#FIXME: check correctness.
class IndicatorBuildDataframe(BaseDataframe):
    def __init__(
            self, 
            _pandas_ExcelFile: pd.ExcelFile, 
            _name_Dataframe: str, 
            _name_ExcelSheet: str = None, 
            _bool_read_df: bool = True, 
            _bool_build_df: bool = False, 
            _read_fillna_value=None
            ) -> None:
        super().__init__(
            _pandas_ExcelFile, 
            _name_Dataframe, 
            _name_ExcelSheet, 
            _bool_read_df, 
            _bool_build_df, 
            _read_fillna_value
            )




class ExecutedOnLineIndicatorDataframe(IndicatorBuildDataframe):
    def __init__(
            self, 
            _pandas_ExcelFile: pd.ExcelFile, 
            _name_Dataframe: str, 
            _name_ExcelSheet: str = None, 
            _bool_read_df: bool = True, 
            _bool_build_df: bool = False, 
            _read_fillna_value=None
            ) -> None:
        super().__init__(
            _pandas_ExcelFile, 
            _name_Dataframe, 
            _name_ExcelSheet, 
            _bool_read_df, 
            _bool_build_df, 
            _read_fillna_value
            )

    def build(
            self, 
            managerDF: ManagerDataframes, 
            keepCols: Union[
                str, 
                list[str]
                ]
            ):
        self.indicatorBuilder(managerDF=managerDF, keepCols=keepCols)



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

dfs = {
        # >>>> Name of instance: ConfigBaseDataframe[...]
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
        'ExecutedOnLineIndicatorDF': ConfigBaseDataframe(
            class_type=ExecutedOnLineIndicatorDataframe,
            read_sheet=False,
            build_indicator_based=True,
            build_keep_columns=['On_line', 'Production_line_specific_line']

            )
    }        

T = TypeVar('T', bound='BaseDataframe')
class ManagerDataframes:
    """This class is used to store different dataframes. It can then be used to fetch or remove certain dataframes based on their name.
    """
    def __init__(self) -> None:
        self.stored_Dataframes = {}

        self.validated_dfs = {}

    def store_Dataframe(
            self,
            dataframe_to_store: Union[
                BaseDataframe, 
                list(BaseDataframe)
                ] = None
        ): 
        """Stores the given dataframes in the ManagerDataframes instance, can be retrieved using the dataframe name.

        Args:
            dataframe_to_store (Union[ BaseDataframe, list, optional): Dataframe(s) to store. Defaults to None.
        """
        if dataframe_to_store:
            if isinstance(dataframe_to_store, list):
                for df in dataframe_to_store:
                    self.store_Dataframe(dataframe_to_store=df)
            
            else:
                name_df = dataframe_to_store._name_Dataframe
                self.stored_Dataframes[name_df] = dataframe_to_store

        else:
            print(f'Dataframe has not been stored since given dataframe_to_store ({dataframe_to_store}) is empty')
            pass

    def remove_Dataframe(
            self, 
            dfs_to_remove: Union[
                list[str], 
                str
                ]
        ):
        """Remove a dataframe in the dictionary.

        Args:
            dfs_to_remove (Union[list[str], str]): Dataframe(s) to remove (Can also be subclass of BaseDataframe)
        """
        if isinstance(dfs_to_remove, str):
            self.remove_Dataframe(dfs_to_check=[dfs_to_remove])
        
        # Check if the DataFrame exists in the dictionary
        self.validate_presence_Dataframe(dfs_to_check=dfs_to_remove)
        
        # Remove the DataFrame
        for df in dfs_to_remove:
            del self.stored_Dataframes[df]
    
    #FIXME: Works, but does not do the correct type hinting. So try to fix that, otherwise return to the previous way as it was more concise.
    def get_Dataframe(
            self,
            dfs_to_get: Union[list[str], str],
            check_pandasDF_presence: bool = True,
            check_clean_status: bool = True,
            expected_return_type: type[T] = BaseDataframe # appears not to be used, but without it the typing does not work when using a result of get_Dataframe(). e.g. indexDF.time_intervals would not be suggested.
    ) -> Union[T, list[T]]:
        """Retrieves dataframe if it is present, if not raises a value error.

        Args:
            dfs_to_get (Union[List[str], str]): df_name(s) to retrieve.
            check_pandasDF_presence (bool): Should a pandasDF be present in order to be retrieved. Defaults to True.
            check_clean_status (bool): Should a pandasDF be cleaned in order to be retrieved. Defaults to True.

        Returns:
            Union[BaseDataframe, List(BaseDataframe)]: Asked for BaseDataframe(s) (subclass)
        """
        def _check_dataframe_type(
                dataframe: BaseDataframe, 
                dataframe_location: int = 0
                ):
            """Check whether the type is correct

            Args:
                dataframe (BaseDataframe): _description_
                dataframe_location (int, optional): location of dataframe in dfs_to_get. Defaults to 0.

            Raises:
                TypeError: If the expected dataframe type is not equal to the actual dataframe type.
            """
            expected_return_type = _get_expected_return_type(dfs_to_get[dataframe_location])
            
            if not issubclass(type(dataframe), expected_return_type):
                raise TypeError(f"Expected dataframe of type: '{expected_return_type}' \n "
                                f"But got dataframe of type: '{type(dataframe)}', for dataframe: '{dataframe}'")

        def _get_expected_return_type(df_name: str) -> type[T]:
            """Get the expected class type of a dataframe by name.

            Args:
                df_name (str): Dataframe name to get expected class from.

            Raises:
                KeyError: If df_name cannot be found in the dfs dictionary.

            Returns:
                type[T]: Expected class_type of the Dataframe.
            """
            if df_name not in dfs.keys():
                raise KeyError(f"The dataframe name: '{df_name}', was not found in the keys of the 'dfs' dictionairy: \n \n '{dfs}'")
            
            return dfs[df_name].class_type
        
        if isinstance(dfs_to_get, str):
            return self.get_Dataframe(
                dfs_to_get=[dfs_to_get],
                expected_return_type=_get_expected_return_type(dfs_to_get)
                )

        # Only validate if df has not yet been checked.
        dfs_to_validate = [df for df in dfs_to_get if df not in self.validated_dfs.keys()]

        # Validate not yet checked dfs
        if dfs_to_validate:
            self._validate_presence_Dataframe(
                dfs_to_check=dfs_to_validate,
                check_pandasDF_presence=check_pandasDF_presence,
                check_clean_status=check_clean_status
            )

        if len(dfs_to_get) == 1:
            df = self.stored_Dataframes[dfs_to_get[0]]
            _check_dataframe_type(dataframe=df)
            return df
        else:
            dataframe_location = 0
            results = []

            for df in dfs_to_get:
                specific_df = self.stored_Dataframes[df]
                _check_dataframe_type(
                    dataframe=specific_df, 
                    dataframe_location=dataframe_location
                    )
                results.append(specific_df)

                dataframe_location += 1

            return results
    
    ### HELPER FUNCTIONS
    def _validate_presence_Dataframe(
            self, 
            dfs_to_check: Union[
                list[str], 
                str
                ] = None, 
            check_clean_status: bool = False, 
            check_pandasDF_presence: bool = False
            ):
        """
        Checks whether the asked dataframe(s) is/are present within the ManagerDataframes. 

        Does not check for None values because the dataframes are being read, so are either an empty dataframe/series or are non empty. Eitherway they will be evaluated after the presence is checked.
        

        Args:
            dfs_to_check (Union[ list[str], str ], optional): _description_. Defaults to None.
            check_clean_status (bool, optional): _description_. Defaults to False.
            check_pandasDF_presence (bool, optional): _description_. Defaults to False.

        Raises:
            AttributeError: If one of the dataframes to check cannot be found within the ManagerDataframes instance.
            AttributeError: _description_
        """
        errors = {}
        correct = {}
        incorrect = {}

        # Create suberror savers
        absent_dfs = []
        found_dfs = []

        found_pd_dfs = []
        absent_pd_dfs = []

        cleaned_dfs = []
        uncleaned_dfs = []

        def __handle_exception(name_df, key, e):
            absent_dfs.append(name_df)
            errors[f"{key}, {name_df}:"] = str(e)

        def __validate_single_dataframe(
                name_df, 
                key, 
                ):
            try:
                self._check_name_in_StoredDataframes(_name_Dataframe=name_df)
                self.validated_dfs[name_df] = self.stored_Dataframes[name_df]
                found_dfs.append(name_df)

                if check_pandasDF_presence:
                    pd_df = self.get_Dataframe(dfs_to_get=[name_df]).pandas_Dataframe

                    if pd_df.empty:
                        absent_pd_dfs.append(name_df)
                    
                    else:
                        found_pd_dfs.append(name_df)

                if check_clean_status and self.get_Dataframe(dfs_to_get=name_df)._status_cleaned:
                    cleaned_dfs.append(name_df)
                elif check_clean_status:
                    uncleaned_dfs.append(name_df)

            except KeyError as e:
                __handle_exception(name_df, key, e)
            except Exception as e:
                __handle_exception(name_df, key, e)

        if isinstance(dfs_to_check, str):
            dfs_to_check = [dfs_to_check]

        for name_df in dfs_to_check:
            __validate_single_dataframe(name_df, "Absent Dataframe")

        # List the correctly executed dfs.
        correct['Found Dataframes'] = found_dfs
        incorrect['Absent Dataframes'] = absent_dfs
        if check_pandasDF_presence:
            correct['Found PANDAS Dataframes'] = found_pd_dfs
            incorrect['Empty PANDAS Dataframes'] = absent_pd_dfs

        if check_clean_status:
            correct['Cleaned Dataframes'] = cleaned_dfs
            incorrect['Uncleaned Dataframes'] = uncleaned_dfs

        if errors:
            raise AttributeError(
                f"While validating the presence of (a) dataframe(s), one or more errors have occurred: \n {', '.join(f'{key}: {value}' for key, value in errors.items())} \n\n The following things did not go as expected: \n{incorrect}. \n\n The following things did go as expected: \n {correct}"
            )
        
    def _check_name_in_StoredDataframes(self, _name_Dataframe: str):
        """Checks whether a name is in the stored dataframes, if not it raises an error and suggests all possible names, but also indicates if there is a name with the same spelling but with different cases, like name and naMe. 

        Args:
            _name_Dataframe (str): df_name to check

        Raises:
            ValueError: If the name cannot be found, suggests other names.
        """
        if _name_Dataframe in self.stored_Dataframes:
            pass
        
        else:
            suggested_similar_names =  self._suggest_names_similar(name=_name_Dataframe)
            suggested_all_names = self._suggest_names_all()
            raise ValueError(f"The given name '{_name_Dataframe}' cannot be found in the stored names. \n Did you mean one of these: {', '.join(suggested_similar_names)}? \n\n If not, select one of the saved names: {', '.join(suggested_all_names)}")
    
    def _suggest_names_similar(self, name: str):
        """Gives the name suggestion for names that have the same letters, but different cases. 
        \n e.g. It would return 'name', if 'name' is a stored df_name, for ['Name', 'nAme', 'NAME', etc.]

        Args:
            name (str): Name to check

        Returns:
            list[str]: stored df_names with same spelling but different cases.
        """
        return [df_name for df_name in self.stored_Dataframes if name.lower() in df_name.lower()]
    
    def _suggest_names_all(self):
        """Gives the name suggestions out of all the names of stored dataframes.

        Returns:
            list[str]: names of stored dataframes.
        """
        return [df_name for df_name in self.stored_Dataframes]
    