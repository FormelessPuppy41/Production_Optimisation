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
            Type[pd.DataFrame], 
            Type[pd.Series]
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
                Type[pd.DataFrame], 
                Type[pd.Series]
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

    def read_Dataframe_fromExcel(self):
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


class ordersDataframe(BaseDataframe):
    def __init__(self) -> None:
        super().__init__()
    
    def clean():
        pass

class ManagerDataframes:
    def __init__(self) -> None:
        pass