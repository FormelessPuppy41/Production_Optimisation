import tkinter as tk
from tkinter import messagebox

from data.excel_file import ExcelFile
from data.dataframe import Dataframe

class Data_Reader:
    def __init__(self, name_excel_file: str, path_excel_file: str):
        self.name_excel_file = name_excel_file
        self.path_excel_file = path_excel_file

        self.excel_file = ExcelFile(name_excel_file=name_excel_file, path_excel_file=path_excel_file)


    def read_all_dataframes(self, sheet_names_to_read: list):
        sheet_names = self.excel_file.get_sheet_names()

        given_sheets_in_excel_file = []
        given_sheets_not_in_excel_file = []
        for sheet in sheet_names_to_read:
            if sheet in sheet_names:
                given_sheets_in_excel_file.append(sheet)
            else:
                given_sheets_not_in_excel_file.append(sheet)
        
        if given_sheets_in_excel_file is None:
            raise ValueError(f'None of the given sheet names in: {sheet_names_to_read} \n are in the Excel file: {self.excel_file} \n in the path: {self.path_excel_file}')
        
        dataframes = []
        for sheet in given_sheets_in_excel_file:
            dataframe = Dataframe(
                name_excel_file=self.name_excel_file, path_excel_file=self.path_excel_file, 
                dataframe_name=f'{sheet}', excel_sheet_name=sheet
                ).read_excel_dataframe()
            dataframes.append(dataframe)

        if given_sheets_not_in_excel_file:
            if given_sheets_in_excel_file:
                message = f'None of the sheets in: {sheet_names_to_read} were found in the Excel file in the path: {self.path_excel_file}'
            message = f'The following sheets: {given_sheets_not_in_excel_file} were not found in the Excel file in the path: {self.path_excel_file}'
            # Show a pop-up message box to the user
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            messagebox.showwarning('Missing Sheets', message)

        return dataframes