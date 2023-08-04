from excel_file import ExcelFile
from dataframe import Dataframe

class Data_Reader:
    def __init__(self, name_excel_file: str, path_excel_file: str):
        self.name_excel_file = name_excel_file
        self.path_excel_file = path_excel_file

        self.excel_file = ExcelFile(name_excel_file=name_excel_file, path_excel_file=path_excel_file)


    def read_all_dataframes(self, sheet_names_to_read: list):
        sheet_names = self.excel_file.get_sheet_names
        checked_sheet_names = [sheet for sheet in sheet_names_to_read if sheet in sheet_names]
        dataframes = []

        if checked_sheet_names is None:
            raise ValueError(f'None of the given sheet names in: {sheet_names_to_read} \n are in the Excel file: {self.excel_file} \n in the path: {self.path_excel_file}')
        for sheet in checked_sheet_names:
            dataframe = Dataframe(
                name_excel_file=self.name_excel_file, path_excel_file=self.path_excel_file, 
                dataframe_name=f'{sheet}', excel_sheet_name=sheet
                ).read_excel_dataframe()
            dataframes.append(dataframe)

        return dataframes