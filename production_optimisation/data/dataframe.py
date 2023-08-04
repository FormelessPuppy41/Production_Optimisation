import pandas as pd
import openpyxl
from excel_file import ExcelFile

class Dataframe(ExcelFile):
    def __init__(self, name_excel_file: str, path_excel_file: str, dataframe_name: str, excel_sheet_name: str):
        super().__init__(name_excel_file=name_excel_file, path_excel_file=path_excel_file) 
        
        self.dataframe_name = dataframe_name
        self.excel_sheet_name = excel_sheet_name
        self.excel_file = super().get_pandas_excel_file()


    def get_name_dataframe(self):
        return self.dataframe_name
    

    def check_sheet_name(self) -> bool:
        if self.excel_sheet_name in self.excel_file.sheet_names:
            return True
        else:
            return False


    def read_excel_dataframe(self):
        if self.check_sheet_name():
            return pd.read_excel(
                io=self.path_excel_file,
                sheet_name=self.excel_sheet_name,
                engine='openpyxl'
            )
        else:
            raise KeyError(f'Sheet name: {self.excel_sheet_name} , not found in the Excel file in path: {self.excel_file_path}')
    
    
