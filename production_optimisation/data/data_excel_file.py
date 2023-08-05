import pandas as pd
import re

class ExcelFile:
    """The ExcelFile class is for 'Storing' a ExcelFile. It has different kind of subclasses that can preform manipulations on Dataframes. 
    """
    def __init__(self, name_excel_file: str, path_excel_file: str):
        """This is a constructor for a ExcelFile

        Args:
            name_excel_file (str): Name of the ExcelFile
            path_excel_file (str): Path to the ExcelFile

        Raises:
            ValueError: If the path does not contain a file ending with '.xlsx'
        """
        if re.search('.xlsx', path_excel_file):
            self.name_excel_file = name_excel_file
            self.path_excel_file = path_excel_file
            self.pandas_excel_file = pd.ExcelFile(self.path_excel_file)
        else:
            raise ValueError(f'No excel file found in directory {self.path_excel_file}')

    def get_pandas_excel_file(self) -> pd.ExcelFile:
        """Gets the pandas.ExcelFile of the ExcelFile

        Returns:
            pd.ExcelFile: The ExcelFile
        """
        return self.pandas_excel_file
    
    def get_path_excel_file(self) -> str:
        """Gets the path to the ExcelFile

        Returns:
            str: The Path to the ExcelFile
        """
        return self.path_excel_file
    
    def get_sheet_names(self) -> list:
        """Gets the names of the sheets in the ExcelFile

        Returns:
            list: List with the names of the sheets in the ExcelFile
        """
        return self.pandas_excel_file.sheet_names
    