import pandas as pd
import openpyxl
from icecream import ic
from typing import Type, Union

from general_configuration import dfs

class BaseDataframe:
    def __init__(
            self, 
            pandas_ExcelFile: pd.ExcelFile, 
            name_Dataframe: str, 
            name_ExcelSheet: str = None,
            name_DataframeType: str = None
            ) -> None:
        
        self.name_Dataframe = name_Dataframe
        self.name_ExcelSheet = name_ExcelSheet
        self.name_DataframeType = name_DataframeType

        self.pandas_ExcelFile  = pandas_ExcelFile
        self.pandas_Dataframe: Union[
            pd.DataFrame, 
            pd.Series
            ] = None

        self.status_cleaned: bool = False
        self.status_stored: bool = False

        self.fillna_value = None

    ### RETRIEVING INFORMATION ABOUT THE DATAFRAME
    # Retrieve names
    def get_name_Dataframe(self) -> str:
        return self.name_Dataframe
    
    def get_name_ExcelSheet(self) -> str:
        return self.name_ExcelSheet
    
    def get_name_DataframeType(self) -> str:
        return self.name_DataframeType
    
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
        self.type_fillna = new_value

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
    def clean():
        """Empty clean function, since cleaning method depends on the Dataframe type.
        """
        pass

    def build():
        """Empty build function, since building method depends on the Dataframe type.
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
            type(equal to the type of the called on Dataframe): The copy instance of the Dataframe.
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
            self.get_cleaned_status()
            )
        
        return new_Dataframe

    ### READING/WRITING DATA FROM/TO EXCEL
    def read_Dataframe_fromExcel(self):
        """Read the dataframe from excel. First validates whether the name of the excelsheet can be found.

        Raises:
            ValueError: Dataframe does not have a value for {name_ExcelSheet}.
            ValueError: Dataframe's {name_ExcelSheet} cannot be found in the sheet_names of the ExcelFile.
        """
        self.validate_name_ExcelSheet()
        
        self.pandas_Dataframe = pd.read_excel(
            io=self.pandas_ExcelFile.io,
            sheet_name=self.name_ExcelSheet,
            engine='openpyxl'
        ).fillna(self.type_fillna)

    def write_Dataframe_toExcel(self):
        """Write the dataframe to excel. First validates whether the name of the excelsheet can be found.

        Raises:
            ValueError: Dataframe does not have a value for {name_ExcelSheet}.
            ValueError: Dataframe's {name_ExcelSheet} cannot be found in the sheet_names of the ExcelFile.
        """
        self.validate_name_ExcelSheet()

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

    ### HELPER FUNCTIONS
    # Validation
    def validate_name_ExcelSheet(self):
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
    def change_index_to_firstCol(self):
        """Changes the index of the dataframe to the first column of the dataframe.
        """
        if not self.pandas_Dataframe.empty:
            columns = self.pandas_Dataframe.columns
            self.pandas_Dataframe = self.pandas_Dataframe.set_index(columns[0])



class ordersDataframe(BaseDataframe):
    """The ordersDataframe is a class that is used to describe the ordersDF.
    Subclass of the BaseDataframe

    Subclass of:
        BaseDataframe: Basic description of Dataframes.
    """
    def __init__(
            self, 
            pandas_ExcelFile: pd.ExcelFile, 
            name_Dataframe: str, 
            name_ExcelSheet: str = None, 
            name_DataframeType: str = None
            ) -> None:
        
        super().__init__(
            pandas_ExcelFile, 
            name_Dataframe, 
            name_ExcelSheet, 
            name_DataframeType
            )

        # During cleaning the description column is excluded to preserve the format.
        self.columns_to_exclude_cleaning = ['Description']
        self.columns_to_clean = self.pandas_Dataframe.columns.drop(self.columns_to_exclude_cleaning)
    
    ### SUBCLASS SPECIFIC FUNCTIONS
    def clean(self):
        """Cleans the orders dataframe by changing all strings to uppercase and otherwise returning the element for the columns that need to be cleaned.
        """
        if not self.status_cleaned: # If the dataframe has not yet been cleaned, clean it.
            for col in self.columns_to_clean:
                self.pandas_Dataframe[col] = self.pandas_Dataframe[col].apply(
                        lambda x: self.clean_orderDF_elements(x)
                        )
                
            self.change_cleaned_status(True)

    #FIXME: Add data validation for missing data.
    def validate_data(self):
        pass

    ### HELPER FUNCTIONS
    def clean_orderDF_elements(self, element):
        """This function cleans the actual elements of each column based on the datatype of the column.
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
            else:
                return element
        else:
            return element
    
        

class indexSetsDataframe(BaseDataframe):
    def __init__(
            self, 
            pandas_ExcelFile: pd.ExcelFile, 
            name_Dataframe: str, 
            name_ExcelSheet: str = None, 
            name_DataframeType: str = None
            ) -> None:
        
        super().__init__(
            pandas_ExcelFile, 
            name_Dataframe, 
            name_ExcelSheet, 
            name_DataframeType
            )

    #TODO: Add getters for all index sets. 
    def get_indexes():
        pass    
        
    def clean(self):
        if not self.status_cleaned:
            self.pandas_Dataframe = self.pandas_Dataframe.apply(
                lambda x: self.clean_indexDF_elements(x)
                )
            
            self.change_cleaned_status(True)
        pass    
    
    ### HELPER FUNCTIONS
    def clean_indexDF_elements(self, element):
        if element and pd.notna(element):
            if isinstance(element, str):
                return element.upper()
            elif isinstance(element, pd.Timestamp):
                return element
            elif isinstance(element, float):
                return int(element)
        else:
            return element



class oldPlanningDataframe(BaseDataframe):
    def __init__(
            self, 
            pandas_ExcelFile: pd.ExcelFile, 
            name_Dataframe: str, 
            name_ExcelSheet: str = None, 
            name_DataframeType: str = None
            ) -> None:
        
        super().__init__(
            pandas_ExcelFile, 
            name_Dataframe, 
            name_ExcelSheet, 
            name_DataframeType
            )

    def clean(self):
        if not self.pandas_Dataframe.empty and not self.status_cleaned:
            columns = self.pandas_Dataframe.columns.to_list()
            index_columns = [idx for idx in columns if columns.index(idx) <= 2]

            self.pandas_Dataframe = self.pandas_Dataframe.set_index(index_columns)
            self.pandas_Dataframe.columns = ['allocation']

            # Drop rows with value 0.0
            self.pandas_Dataframe = self.pandas_Dataframe[self.pandas_Dataframe != 0.0]

            self.change_cleaned_status(True)
    


class manualPlanningDataframe(BaseDataframe):
    def __init__(
            self, 
            pandas_ExcelFile: pd.ExcelFile, 
            name_Dataframe: str, 
            name_ExcelSheet: str = None, 
            name_DataframeType: str = None
            ) -> None:
        
        super().__init__(
            pandas_ExcelFile, 
            name_Dataframe, 
            name_ExcelSheet, 
            name_DataframeType
            )
        

    def clean(self):
        if not self.pandas_Dataframe.empty and not self.status_cleaned:
            self.pandas_Dataframe = self.pandas_Dataframe.rename_axis('time', axis=1)

            self.pandas_Dataframe = self.pandas_Dataframe.stack()
            self.pandas_Dataframe.name = 'allocation'
            
            # Drop rows with value 0.0
            self.pandas_Dataframe = self.pandas_Dataframe[self.pandas_Dataframe != 0.0]

            self.pandas_Dataframe = self.pandas_Dataframe.reorder_levels(
                ['order_suborder','time', 'empl_line']
                )
            
            self.change_cleaned_status(True)



class ManagerDataframes:
    def __init__(self) -> None:
        self.stored_Dataframes = []
        
    def store_Dataframe(
            self,
            dataframe_to_store: BaseDataframe
            ):
        if not dataframe_to_store.get_status_stored():
            self.stored_Dataframes.append(dataframe_to_store)
    
    def remove_Dataframe(
            self, 
            dataframe_to_delete: BaseDataframe
        ):
        self.stored_Dataframes.remove(dataframe_to_delete)