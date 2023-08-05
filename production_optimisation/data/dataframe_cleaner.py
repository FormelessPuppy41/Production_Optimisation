from data.dataframe import Dataframe


class Dataframe_Cleaner(Dataframe):

    def __init__(self, name_excel_file: str, path_excel_file: str, dataframe_name: str, excel_sheet_name: str):
        super().__init__(name_excel_file=name_excel_file, path_excel_file=path_excel_file, dataframe_name=dataframe_name)
        
        self.name_excel_file = name_excel_file
        self.path_excel_file = path_excel_file
        self.excel_sheet_name = excel_sheet_name

        
