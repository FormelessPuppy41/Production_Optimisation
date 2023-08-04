import pandas as pd

class ExcelFile:
    def __init__(self, name_excel_file: str, path_excel_file: str):
        self.name_excel_file = name_excel_file
        self.path_excel_file = path_excel_file
        self.pandas_excel_file = pd.ExcelFile(io=self.path_excel_file)

    def get_pandas_excel_file(self) -> pd.ExcelFile:
        return self.pandas_excel_file
    
    def get_path_excel_file(self) -> str:
        return self.path_excel_file
    
    def get_sheet_names(self) -> list:
        return self.pandas_excel_file.sheet_names
    