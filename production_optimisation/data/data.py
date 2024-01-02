from __future__ import annotations 
# Used in building dataframes, since the ManagerDataframes is located at the end of the file. 
# Subsequent of all DF's that are build and need a ManagerDataframe as input

import pandas as pd
import numpy as np
import openpyxl
from icecream import ic
from typing import Union


class BaseDataframe:
    """_summary_
    """
    def __init__(
            self, 
            pandas_ExcelFile: pd.ExcelFile, 
            name_Dataframe: str, 
            name_ExcelSheet: str = None,
            bool_read_df: bool = True,
            bool_build_df: bool = False, 
            fillna_value = None
            ) -> None:
        
        self.name_Dataframe = name_Dataframe
        self.name_ExcelSheet = name_ExcelSheet
        
        self.bool_read_df = bool_read_df 
        self.bool_build_df = bool_build_df

        self.pandas_ExcelFile  = pandas_ExcelFile
        self.pandas_Dataframe: Union[
            pd.DataFrame, 
            pd.Series
            ] = pd.DataFrame()

        self.status_cleaned: bool = False
        self.status_stored: bool = False

        if not fillna_value:
            self.fillna_value = ''
        else:
            self.fillna_value = fillna_value

    ### RETRIEVING INFORMATION ABOUT THE DATAFRAME
    # Retrieve names
    def get_name_Dataframe(self) -> str:
        return self.name_Dataframe
    
    def get_name_ExcelSheet(self) -> str:
        return self.name_ExcelSheet
    
    # Retrieve pandas
    def get_pandas_ExcelFile(self) -> pd.ExcelFile:
        return self.pandas_ExcelFile
    
    def get_pandas_Dataframe(self) -> pd.DataFrame:
        return self.pandas_Dataframe
    
    # Retrieve status
    def get_status_cleaned(self) -> bool:
        return self.status_cleaned
    
    def get_status_stored(self) -> bool:
        return self.status_stored
    
    def get_type_fillna(self):
        return self.fillna_value

    ### CHANGE SPECIFIC ATTRIBUTES OF AN INSTANCE OF THE OBJECT
    # Change Status
    def change_cleaned_status(
            self, 
            new_status: bool
            ):
        """Changes the cleaned status of the dataframe to {new_status} to indicate whether the dataframe has been cleaned or not.

        Args:
            new_status (bool): True if cleaned, False if not cleaned.
        """
        self.status_cleaned = new_status
    
    def change_stored_status(
            self,
            new_status: bool
            ):
        """Changes the stored status of the dataframe to {new_status} to indicate whether the dataframe has been stored or not.

        Args:
            new_status (bool): True if stored, False if not stored.
        """
        self.status_stored = new_status

    # Change values
    def change_fillna_value(
            self, 
            new_value
            ):
        """Changes the value that the NaN values are filled with. 

        Args:
            new_value (_type_): The new value which fills the NaN values.
        """
        if not new_value:
            self.fillna_value = ''
        else:
            self.fillna_value = new_value

    # Change pandas
    def change_pandas_Dataframe(
            self, 
            changed_Dataframe: Union[
                pd.DataFrame, 
                pd.Series
                ]
            ):
        """Changes the pd.DataFrame/pd.Series to {changed_Dataframe}. 

        Args:
            changed_Dataframe (Union[ Type[pd.DataFrame], Type[pd.Series] ]): The pd.DataFrame/Series to change the current pandas_Dataframe to.
        """
        self.pandas_Dataframe = changed_Dataframe

    # Change name
    def change_name_ExcelSheet(
            self, 
            name_new_ExcelSheet: str
            ):
        """Changes the name of the excel sheet where the dataframe can be found or should be written to {name_new_ExcelSheet}

        Args:
            name_new_ExcelSheet (str): Name of the new excel_sheet where the dataframe can be found or should be written to.
        """
        self.name_ExcelSheet = name_new_ExcelSheet

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
            self.pandas_ExcelFile, 
            name_new_Dataframe, 
            self.name_ExcelSheet
            )
        
        # Change the pandas dataframe to be the same as the original
        new_Dataframe.change_pandas_Dataframe(
            self.pandas_Dataframe
            )
        
        # If the original was already cleaned, then the status of new df should also be True, else it will be False.
        new_Dataframe.change_cleaned_status(
            self.status_cleaned
            )
        
        return new_Dataframe

    ### READING/WRITING DATA FROM/TO EXCEL
    def read_Dataframe_fromExcel(self):
        """Read the dataframe from excel, if indicated in df declaration that it is needed (bool_read_df). 
        \n Validates whether the name of the excelsheet can be found.

        Raises:
            ValueError: Dataframe does not have a value for {name_ExcelSheet}.
            ValueError: Dataframe's {name_ExcelSheet} cannot be found in the sheet_names of the ExcelFile.
        """
        if self.bool_read_df:
            self._validate_name_ExcelSheet()
            
            self.pandas_Dataframe = pd.read_excel(
                io=self.pandas_ExcelFile.io,
                sheet_name=self.name_ExcelSheet,
                engine='openpyxl'
            ).fillna(self.fillna_value)

    #FIXME: Create VBA file that communicates with python to indicate whether a file is opened by the user, then the dataframe will not be written to excel until the file is closed. otherwise there will be alot of corrupt files.
    def write_Dataframe_toExcel(self):
        """Write the dataframe to excel. 
        \n Validates whether the name of the excelsheet can be found.

        Raises:
            ValueError: Dataframe does not have a value for {name_ExcelSheet}.
            ValueError: Dataframe's {name_ExcelSheet} cannot be found in the sheet_names of the ExcelFile.
        """
        self._validate_name_ExcelSheet()

        # Use pd.ExcelWriter as a Writer, to write the excelfile to a sheet in the ExcelFile.
        with pd.ExcelWriter(
            path=self.pandas_ExcelFile.io, 
            mode='a', 
            if_sheet_exists='replace', 
            engine='openpyxl', 
            engine_kwargs={'keep_vba': True}
            ) as writer:

            self.pandas_Dataframe.to_excel(
                excel_writer=writer, 
                sheet_name=self.name_ExcelSheet, 
                index=True
                )
        
        ic(f'Dataframe ({self.name_Dataframe}) written to ExcelFile in sheet ({self.name_ExcelSheet}) correctly.')

    #FIXME: Add data validation for missing data. Same for other dataframes that have index sets as input, are they the correct format?
    def validate_data(self):
        pass

    ### HELPER FUNCTIONS
    # Validation
    def _validate_name_ExcelSheet(self):
        """Validate whether the name of the ExcelSheet can be found in the sheet_names of the ExcelFile.

        Raises:
            ValueError: Dataframe does not have a value for {name_ExcelSheet}.
            ValueError: Dataframe's {name_ExcelSheet} cannot be found in the sheet_names of the ExcelFile.
        """
        # If there is no excel sheet name
        if self.name_ExcelSheet is None:
            raise ValueError(
                f'Dataframe ({self.name_Dataframe}) does not have its own sheet in the ExcelFile ({self.pandas_ExcelFile})'
                )
        
        # If the given sheet_name cannot be found in the corresponding ExcelFile. 
        elif self.name_ExcelSheet not in self.pandas_ExcelFile.sheet_names:
            raise ValueError(
                f'The given sheetname ({self.name_ExcelSheet}) for the dataframe ({self.name_Dataframe}) cannot be found in the sheet_names within the given ExcelFile ({self.pandas_ExcelFile})'
                )
        
        # If the given sheet_name can be found in the given ExcelFile.
        elif self.name_ExcelSheet in self.pandas_ExcelFile.sheet_names:
            pass
    
    # Frame manipulations
    def _change_index_to_firstCol(self):
        """Changes the index of the dataframe to the first column of the dataframe.
        """
        if not self.pandas_Dataframe.empty:
            columns = self.pandas_Dataframe.columns
            self.pandas_Dataframe = self.pandas_Dataframe.set_index(columns[0])



class OrderDataframe(BaseDataframe):
    """The ordersDataframe is a class that is used to describe the ordersDF.

    Subclass of:
        BaseDataframe: Basic description of Dataframes.
    """
    def __init__(
            self, 
            pandas_ExcelFile: pd.ExcelFile, 
            name_Dataframe: str, 
            name_ExcelSheet: str = None, 
            bool_read_df: bool = True, 
            fillna_value = None
            ) -> None:
        
        super().__init__(
            pandas_ExcelFile, 
            name_Dataframe, 
            name_ExcelSheet, 
            bool_read_df,
            fillna_value
            )

    ### SUBCLASS SPECIFIC FUNCTIONS
    def clean(self):
        """Cleans the orders dataframe by changing all strings to uppercase and otherwise returning the element for the columns that need to be cleaned.

        str -> uppercase
        else -> element
        """
        # Check if the dataframe has not yet been cleaned, if so, clean it.
        if not self.status_cleaned:
            self._change_index_to_firstCol()  

            # During cleaning the description column is excluded to preserve the format.
            columns_to_exclude_cleaning = ['Description']
            columns_to_clean = self.pandas_Dataframe.columns.drop(columns_to_exclude_cleaning)
            
            # Clean individual column elements
            for col in columns_to_clean:
                self.pandas_Dataframe[col] = self.pandas_Dataframe[col].apply(
                        lambda x: self._clean_orderDF_elements(x)
                        )
            
            # Remove empty rows
            self.pandas_Dataframe = self.pandas_Dataframe[self.pandas_Dataframe != '']
            self.pandas_Dataframe.fillna(self.fillna_value)
            
            self.change_cleaned_status(True)

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
            pandas_ExcelFile: pd.ExcelFile, 
            name_Dataframe: str, 
            name_ExcelSheet: str = None, 
            bool_read_df: bool = True,
            fillna_value = None
            ) -> None:
        
        super().__init__(
            pandas_ExcelFile, 
            name_Dataframe, 
            name_ExcelSheet, 
            bool_read_df,
            fillna_value
            )

    ### RETRIEVE SPECIFIC INDEX SETS
    def get_orders_suborder_set(self):
        return self.pandas_Dataframe['Orders_suborders']
    
    def get_orders_set(self):
        return self.pandas_Dataframe['Orders']
    
    def get_suborders_set(self):
        return self.pandas_Dataframe['Sub_orders']
    
    def get_time_intervals_set(self):
        return self.pandas_Dataframe['Time_intervals']
    
    def get_employee_line_set(self):
        return self.pandas_Dataframe['Employee_line']
    
    def get_employee_set(self):
        return self.pandas_Dataframe['Employees']
    
    def get_employee_set(self):
        return self.pandas_Dataframe['Production_lines']
    
    def clean(self):
        """Clean the indexDF by changing all strings to uppercase, timestamp is left as it is, floats are made to integer.

        str -> uppercase
        pd.timestamp -> element
        float -> int
        """
        if not self.status_cleaned:
            for col in self.pandas_Dataframe.columns:
                self.pandas_Dataframe[col] = self.pandas_Dataframe[col].apply(
                    lambda x: self._clean_indexDF_elements(x)
                    )
            
            self.change_cleaned_status(True)    

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



class OldPlanningDataframe(BaseDataframe):
    """The oldPlanningDataframe is a class that is used to describe the oldPlanningDF.

    Subclass of:
        BaseDataframe: Basic description of Dataframes.
    """
    def __init__(
            self, 
            pandas_ExcelFile: pd.ExcelFile, 
            name_Dataframe: str, 
            name_ExcelSheet: str = None, 
            bool_read_df: bool = True,
            fillna_value = None
            ) -> None:
        
        super().__init__(
            pandas_ExcelFile, 
            name_Dataframe, 
            name_ExcelSheet, 
            bool_read_df,
            fillna_value
            )

    def clean(self):
        """Clean the oldPlanningDF by changing all strings to uppercase, timestamp is left as it is, floats are made to integer.

        str -> uppercase
        pd.timestamp -> element
        float -> int
        """
        if not self.pandas_Dataframe.empty and not self.status_cleaned:
            columns = self.pandas_Dataframe.columns.to_list()
            index_columns = [idx for idx in columns if columns.index(idx) <= 2]

            self.pandas_Dataframe = self.pandas_Dataframe.set_index(index_columns)
            self.pandas_Dataframe.columns = ['allocation']

            # Change format to pd.Series
            self.pandas_Dataframe = self.pandas_Dataframe.iloc[:, 0]

            # Drop rows with value 0.0
            self.pandas_Dataframe = self.pandas_Dataframe[self.pandas_Dataframe != 0.0]

            self.change_cleaned_status(True) 


class ManualPlanningDataframe(BaseDataframe):
    """The oldPlanningDataframe is a class that is used to describe the oldPlanningDF.

    Subclass of:
        BaseDataframe: Basic description of Dataframes.
    """
    def __init__(
            self, 
            pandas_ExcelFile: pd.ExcelFile, 
            name_Dataframe: str, 
            name_ExcelSheet: str = None, 
            bool_read_df: bool = True,
            fillna_value = None
            ) -> None:
        
        super().__init__(
            pandas_ExcelFile, 
            name_Dataframe, 
            name_ExcelSheet, 
            bool_read_df,
            fillna_value
            )

    def clean(self):
        """Clean the manualPlanningDataframe by changing all strings to uppercase, timestamp is left as it is, floats are made to integer.

        str -> uppercase
        pd.timestamp -> element
        float -> int
        """
        if not self.pandas_Dataframe.empty and not self.status_cleaned:
            # Change index to first two columns. (order_suborder, empl_line)
            index_columns = self.pandas_Dataframe.columns.to_list()[:2]
            self.pandas_Dataframe = self.pandas_Dataframe.set_index(index_columns)
            
            # Rename the datestamp columns to 'time'
            self.pandas_Dataframe = self.pandas_Dataframe.rename_axis('time', axis=1)
            
            # Stack columns to get a pd.Series and rename the index.
            self.pandas_Dataframe = self.pandas_Dataframe.stack()
            self.pandas_Dataframe.name = 'allocation'

            # Reorder the index
            self.pandas_Dataframe = self.pandas_Dataframe.reorder_levels(
                ['order_suborder','time', 'empl_line']
                )

            # Replace Empty values ('') to 0.0
            self.pandas_Dataframe = self.pandas_Dataframe.replace('', 0.0)
            
            # Drop rows with value 0.0
            self.pandas_Dataframe = self.pandas_Dataframe[self.pandas_Dataframe != 0.0]
            
            self.change_cleaned_status(True)


class AvailabilityDataframe(BaseDataframe):
    def __init__(
            self, 
            pandas_ExcelFile: pd.ExcelFile, 
            name_Dataframe: str, 
            name_ExcelSheet: str = None, 
            bool_read_df: bool = True, 
            fillna_value = None
            ) -> None:
        super().__init__(
            pandas_ExcelFile, 
            name_Dataframe, 
            name_ExcelSheet, 
            bool_read_df,
            fillna_value
            )
    
    def clean(self):
        """Cleans the AvailabilityDataframe, that is change index to the first column.
        """
        if not self.status_cleaned:
            self._change_index_to_firstCol()

            self.change_cleaned_status(True)



class SkillDataframe(BaseDataframe):
    def __init__(
            self, 
            pandas_ExcelFile: pd.ExcelFile, 
            name_Dataframe: str, 
            name_ExcelSheet: str = None, 
            bool_read_df: bool = True,
            fillna_value = None
            ) -> None:
        super().__init__(
            pandas_ExcelFile, 
            name_Dataframe, 
            name_ExcelSheet, 
            bool_read_df,
            fillna_value
            )
    
    def clean(self):
        """Cleans the skillDataframe, that is change index to the first column.
        """
        if not self.status_cleaned:
            self._change_index_to_firstCol()

            self.change_cleaned_status(True)


### DATAFRAMES THAT ARE BUILD

class CombinedPlanningDataframe(BaseDataframe):
    def __init__(
            self, 
            pandas_ExcelFile: pd.ExcelFile, 
            name_Dataframe: str, 
            name_ExcelSheet: str = None, 
            bool_read_df: bool = True, 
            bool_build_df: bool = False, 
            fillna_value=None
            ) -> None:
        super().__init__(
            pandas_ExcelFile, 
            name_Dataframe, 
            name_ExcelSheet, 
            bool_read_df, 
            bool_build_df, 
            fillna_value
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
        oldPlanningDF: pd.DataFrame
        manualPlanningDF: pd.DataFrame

        # Validate whether the dataframes are actually in the ManagerDataframes.
        oldPlanningDF, manualPlanningDF = self._validate_presence_old_manual_planning(managerDF=managerDF)
        
        combinedPlanningDF: pd.DataFrame = pd.DataFrame()

        # Get the oldPlanningDF that satisfies the condition. That is, is allocated before limit_oldPlanning
        oldPlanningDF = self._apply_oldPlanning_condition(oldPlanningDF=oldPlanningDF)

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
        
        self.pandas_Dataframe = combinedPlanningDF

    # HELPER FUNCTIONS
    #FIXME: Change this to new validate function in ManagerDataframes.
    def _validate_presence_old_manual_planning(self, managerDF: ManagerDataframes) -> list[pd.DataFrame]:
        """Checks whether the OldPlanningDf and ManualPlanningDF are present within the ManagerDataframes. 
        Does not check for None values because the dataframes are being read, so are either an empty dataframe/series or are non empty. Eitherway they will be evaluated after the presence is checked.

        Args:
            managerDF (ManagerDataframes): Manager of the Dataframes.

        Raises:
            AttributeError: If either the OldPlanningDF or ManualPlanningDF Attribute cannot be found within the ManagerDataframe instance.

        Returns:
            [pd.DataFrame, pd.DataFrame]: OldPlanningDF, ManualPlanningDF
        """
        try: 
            oldPlanningDF = managerDF.get_Dataframe('OldPlanningDF').get_pandas_Dataframe()
            manualPlanningDF = managerDF.get_Dataframe('ManualPlanningDF').get_pandas_Dataframe()
            # TODO: add statuscleaned check and clean if necessary?
            return oldPlanningDF, manualPlanningDF
        except:
            raise AttributeError(
                f"Dataframes could not be found within the given ManagerDataframes instance '{managerDF}', for the 'OldPlanningDF' and 'ManualPlanningDF' dataframes. \n Possible cause could be the calling CombinedPlanningDF.build() before having read the PlanningDFs."
            )
    
    def _apply_oldPlanning_condition(self, oldPlanningDF: pd.DataFrame) -> pd.DataFrame:
        """Applies the oldPlanning condition, where only allocations before the limit_OldPlanning are considered. 

        Args:
            oldPlanningDF (pd.DataFrame): OldPlanningDF that shows all the previous allocations.

        Returns:
            pd.DataFrame: OldPlanningDF with only allocations satisfying the condition.
        """
        
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
            self, pandas_ExcelFile: pd.ExcelFile, 
            name_Dataframe: str, 
            name_ExcelSheet: str = None, 
            bool_read_df: bool = True, 
            bool_build_df: bool = False, 
            fillna_value=None
            ) -> None:
        super().__init__(
            pandas_ExcelFile, 
            name_Dataframe, 
            name_ExcelSheet, 
            bool_read_df, 
            bool_build_df, 
            fillna_value
            )
    
    def build():
        pass
    


#FIXME: check correctness.
class IndicatorBuildDataframe(BaseDataframe):
    def __init__(
            self, 
            pandas_ExcelFile: pd.ExcelFile, 
            name_Dataframe: str, 
            name_ExcelSheet: str = None, 
            bool_read_df: bool = True, 
            bool_build_df: bool = False, 
            fillna_value=None
            ) -> None:
        super().__init__(
            pandas_ExcelFile, 
            name_Dataframe, 
            name_ExcelSheet, 
            bool_read_df, 
            bool_build_df, 
            fillna_value
            )
    
    def indicatorBuilder(
            self, 
            managerDF: ManagerDataframes,  
            keepCols: list[str]
            ):
        
        managerDF.validate_presence_Dataframe(
            dfs_to_check = 'OrderDF', 
            check_pandasDF_presence = True, 
            check_clean_status = True
            )

        orderDF = managerDF.get_Dataframe('OrderDF').get_pandas_Dataframe().copy()
        
        # Get columns to drop.
        drop_cols = [
            col 
            for col in orderDF.columns 
            if col not in keepCols
            ]
        
        newDF = orderDF.drop(columns=drop_cols)

        # Make Indicator:
        indicator = np.where(
            newDF.iloc[0] == 1 
            or newDF.iloc[0] == True, 
            [True, False]
            )
        
        newDF = pd.DataFrame(
            indicator, 
            index=newDF.index
            )
        
        self.pandas_Dataframe = newDF
    

class ManagerDataframes:
    """This class is used to store different dataframes. It can then be used to fetch or remove certain dataframes based on their name.
    """
    def __init__(self) -> None:
        self.stored_Dataframes = {}

    #FIXME: Add documentation and change to union[list[str], str]
    def store_Dataframe(
            self,
            dataframe_to_store: BaseDataframe = None
        ): 
        if dataframe_to_store:
            name_df = dataframe_to_store.name_Dataframe
            self.stored_Dataframes[name_df] = dataframe_to_store
        
        else:
            print(f'Dataframe has not been stored since given dataframe_to_store ({dataframe_to_store}) is empty')
            pass

    def remove_Dataframe(
            self, 
            dfs_to_remove: Union[list[str], str]
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
    
    #FIXME: Don't know if making it union and return list works, because now .get.pandasdf() does not look like it works, how to fix.
    def get_Dataframe(
            self, 
            dfs_to_get: Union[list[str], str]
        ) -> list(BaseDataframe):
        """Retrieves dataframe if it is present, if not raises a value error.

        Args:
            dfs_to_get (Union[list[str], str]): df_name(s) to retrieve.

        Returns:
            list(BaseDataframe): Asked for BaseDataframe(s) (subclass)
        """
        if isinstance(dfs_to_get, str):
            self.get_Dataframe(dfs_to_get=[dfs_to_get])

        self.validate_presence_Dataframe(name_Dataframe=dfs_to_get)    
        
        dfs = []
        for df in dfs_to_get:
            dfs.append(df)

        return dfs
    
    #FIXME: Check me
    def validate_presence_Dataframe(
            self, 
            dfs_to_check: Union[
                list(str), 
                str
                ] = None, 
            check_clean_status: bool = False, 
            check_pandasDF_presence: bool = False, 
            check_NoneValues: bool = False
            ):
        """Checks whether the asked dataframe(s) is/are present within the ManagerDataframes. 

        Does not check for None values because the dataframes are being read, so are either an empty dataframe/series or are non empty. Eitherway they will be evaluated after the presence is checked.

        Args:
            managerDF (ManagerDataframes): Manager of the Dataframes.

        Raises:
            AttributeError: If one of the dataframes to check cannot be found within the ManagerDataframes instance.

        """
        # Create errors savers
        errors = {}
        correct = {}

        # Create suberror savers
        absent_dfs = []
        found_dfs = []

        absent_pd_dfs = []
        found_pd_dfs = []

        uncleaned_dfs = []
        cleaned_dfs = []

        noneValues_dfs = []
        values_dfs = []
        
        if isinstance(dfs_to_check, str):
            self.validate_presence_Dataframe(
                dfs_to_check=[dfs_to_check], 
                check_clean_status=check_clean_status, 
                check_pandasDF_presence=check_pandasDF_presence
                )

        else:
            for name_df in dfs_to_check:
                try:
                    # Try retrieving, storing not necessary.
                    self._check_name_in_StoredDataframes(name_Dataframe=name_df)
                    found_dfs.append(name_df)
                
                except Exception as e:
                    absent_dfs.append(name_df)
                    errors[f"Absent Dataframe, {name_df}:"] = e
            
            #errors['Absent Dataframes'] = absent_dfs
            correct['Found Dataframes'] = found_dfs
            
            if check_pandasDF_presence:
                for name_df in found_dfs:
                    try:
                        pd_df = self.get_Dataframe(name_Dataframe=name_df).get_pandas_Dataframe()
                        found_pd_dfs.append(name_df)

                        # If pandas values need to be checked on NoneValues
                        if check_NoneValues:
                            if pd_df:
                                values_dfs.append(name_df)
                            else:
                                noneValues_dfs.append(name_df)
                            
                    except Exception as e:
                        absent_pd_dfs.append(name_df)
                        errors[f"Absent PANDAS Dataframe, {name_df}:"] = e

                #errors['Absent PANDAS Dataframes'] = absent_pd_dfs
                correct['Found PANDAS Dataframes'] = found_dfs

                if check_NoneValues:
                    errors['None Valued PANDAS Dataframes'] = noneValues_dfs
                    correct['Valued PANDAS Dataframes'] = values_dfs

            if check_clean_status:
                for name_df in found_dfs:
                    if self.get_Dataframe(name_Dataframe=name_df).status_cleaned:
                        cleaned_dfs.append(name_df)
                    
                    else:
                        uncleaned_dfs.append(name_df)
                
                errors['Uncleaned Dataframes'] = uncleaned_dfs
                correct['Cleaned Dataframes'] = cleaned_dfs

            if errors:
                raise AttributeError(
                    f" \
                    While validating the presence of (a) dataframe(s) one or more errors have occured: 
                    \n {', '.join(f'{key}: {str(value)}' for key, value in errors.items())} \
                    \n \
                    The following things went as expected: \
                    \n {correct}
                    "
                )
        
    ### HELPER FUNCTIONS
    def _check_name_in_StoredDataframes(self, name_Dataframe: str):
        """Checks whether a name is in the stored dataframes, if not it raises an error and suggests all possible names, but also indicates if there is a name with the same spelling but with different cases, like name and naMe. 

        Args:
            name_Dataframe (str): df_name to check

        Raises:
            ValueError: If the name cannot be found, suggests other names.
        """
        if name_Dataframe in self.stored_Dataframes:
            pass
        
        else:
            suggested_similar_names =  self._suggest_names_similar(name=name_Dataframe)
            suggested_all_names = self._suggest_names_all()
            raise ValueError(f"The given name '{name_Dataframe}' cannot be found in the stored names. \n Did you mean one of these: {', '.join(suggested_similar_names)}? \n If not, select one of the saved names: {', '.join(suggested_all_names)}")
    
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
    