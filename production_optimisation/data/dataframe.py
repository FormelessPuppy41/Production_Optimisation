import pandas as pd
import openpyxl

from data.data_excel_file import ExcelFile

class Dataframe:
    """The Dataframe class is for dataframes that are read from the (parent class) ExcelFile. 

    Args:
        ExcelFile (Parent Class): The parent class
    """
    def __init__(self, excel_file: ExcelFile, dataframe_name: str, excel_sheet_name: str):
        """This is the constructor for the Dataframe class.

        Args:
            name_excel_file (str): Name of the ExcelFile
            path_excel_file (str): Path to the ExcelFile
            dataframe_name (str): Name of the Dataframe
            excel_sheet_name (str): Name of the sheet which contains the Dataframe
        """ 
        self.dataframe_name = dataframe_name
        self.excel_sheet_name = excel_sheet_name
        self.excel_file = excel_file

        self.pandas_excel_file = excel_file.get_pandas_excel_file()
        self.pandas_dataframe = pd.DataFrame

        self.cleaned = False


    def get_name_dataframe(self) -> str:
        """Gets the name of the Dataframe.

        Returns:
            str: Name of the Dataframe
        """
        return self.dataframe_name
    

    def check_sheet_name_in_excelfile(self) -> bool:
        """Checks whether {self.excel_sheet_name} is inside the sheets of the parent ExcelFile.

        Returns:
            bool: True or False // Is inside the parent ExcelFile or not
        """
        if self.excel_sheet_name in self.pandas_excel_file.sheet_names:
            return True
        else:
            return False


    def read_excel_dataframe(self):
        """Read the Dataframe in the {self.excel_sheet_name} sheet in the ExcelFile.

        Raises:
            KeyError: Indicated that the sheet is not found in the sheets of the ExcelFile
        """
        if self.check_sheet_name_in_excelfile():
            self.pandas_dataframe = pd.read_excel(
                io=self.excel_file.get_path_excel_file(),
                sheet_name=self.excel_sheet_name,
                engine='openpyxl'
            ).fillna('')
        else:
            raise KeyError(f'Sheet name: {self.excel_sheet_name} , not found in the Excel file in path: {self.excel_file_path}')
    
    
    def get_pandas_dataframe(self) -> pd.DataFrame:
        """Gets the pandas.DataFrame of the Dataframe.

        Returns:
            pd.DataFrame: The pd.DataFrame version of Dataframe
        """
        if self.pandas_dataframe.empty:
            self.read_excel_dataframe()
                
        return self.pandas_dataframe
    

    def change_status_to_cleaned(self):
        """Changes the indicator that says that a dataframe is not yet cleaned to True, meaning it now is cleaned.
        """
        self.cleaned = True

    
    def get_cleaned_status(self) -> bool:
        """Gets the indicator whether or not a dataframe has been cleaned.

        Returns:
            bool: True - Cleaned or False - Uncleaned
        """
        return self.cleaned

    
    def change_pandas_dataframe(self, new_pandas_df: pd.DataFrame):
        """Changes the current pandas dataframe to a new dataframe, for example a cleaned dataframe.

        Args:
            new_pandas_df (pd.DataFrame): The new DataFrame
        """
        self.pandas_dataframe = new_pandas_df

