import tkinter as tk
from tkinter import messagebox
from typing import List
import pandas as pd

from data.data_excel_file import ExcelFile
from data.dataframe import Dataframe
from general_configuration import sheet_types


class Data_Reader:
    """The Data_Reader class is for reading all the dataframes in a ExcelFile in a given path (to the excelfile). 
    This can be done with the method: "read_all_dataframes".
    """
    def __init__(self, name_excel_file: str, path_excel_file: str):
        """This is a constructor for a Data_Reader.

        Args:
            name_excel_file (str): Name for the excelfile (Does not have to be the .xlsx name)
            path_excel_file (str): Path to the Excel File.
        """
        self.name_excel_file = name_excel_file
        self.path_excel_file = path_excel_file

        self.excel_file = ExcelFile(name_excel_file=name_excel_file, path_excel_file=path_excel_file)
        self.dataframes: List[Dataframe] = []


    def read_all_dataframes(self, sheet_names_to_read: list):
        """This is a function that reads all sheets in the Excel_File that are in the {sheet_names_to_read} list.
        IF a sheet or multiple sheets are not found in the Excel_File then the user gets an error message stating which sheet(s) are not found.
        Then the user can try to fix the error.

        Args:
            sheet_names_to_read (list): Sheets that should be read, They need to be in a 'dataframe' format.

        Raises:
            ValueError: If non of the sheets are found in the Excel_File then there is a ValueError being thrown, which gives the
            message that non of the sheets are found in the File.

        """
        sheet_names = self.excel_file.get_sheet_names()

        # Check whether sheets are in the actual ExcelFile and divide them over two lists, one where they are present
        # and one where they are not present.
        given_sheets_in_excel_file = []
        given_sheets_not_in_excel_file = []
        for sheet in sheet_names_to_read:
            if sheet in sheet_names:
                given_sheets_in_excel_file.append(sheet)
            else:
                given_sheets_not_in_excel_file.append(sheet)
        
        if given_sheets_in_excel_file is None:
            raise ValueError(f'None of the given sheet names in: {sheet_names_to_read} \n are in the Excel file: {self.excel_file} \n in the path: {self.path_excel_file}')

        # Give the user a pop up message if sheet_name(s) are not found.
        if given_sheets_not_in_excel_file: # If given_sheets_not_in_excel_file is not None then: (thus if there are sheets that are not found in the Excelfile)
            if given_sheets_in_excel_file: # If given_sheets_in_excel_file is not None then: (thus if there are sheets that are found in the ExcelFile)
                message = f'WARNING: \n\n The following sheets: \n\n {given_sheets_not_in_excel_file} \n\n Were not found in the Excel file in the Path: \n\n {self.path_excel_file}'
            else:
                message = f'WARNING: \n\n None of the sheets in: \n\n {sheet_names_to_read} \n\n Were found in the Excel file in the Path: \n\n {self.path_excel_file}'
            # Show a pop-up message box to the user
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            messagebox.showwarning('Missing Sheets:', message)

        # Reading the Dataframes and adding them to the dataframes list.
        dataframes = []
        for sheet in given_sheets_in_excel_file:
            
            dataframe = Dataframe(
                excel_file=self.excel_file, dataframe_name=f'{sheet}', excel_sheet_name=sheet
                )
            dataframe.read_excel_dataframe()
            
            dataframes.append(dataframe)

        self.dataframes = dataframes


    def get_dataframes(self) -> List[Dataframe]:
        """Gets the read dataframes, gives back ValueError if they have not been read yet.

        Raises:
            ValueError: Indicates that the dataframes have not yet been used.

        Returns:
            List[Dataframe]: List of the Dataframe's
        """
        if self.dataframes:
            return self.dataframes
        else:
            raise ValueError(f'Dataframes have not yet been read. First use read_all_dataframes() before calling get_dataframes()')
        
    
    def get_sheets_to_read(self, df_with_sheets: Dataframe) -> List[str]:
        """This function can be called after reading the 'helper_read_sheets' dataframe. 
        The sheets in the dataframe are then selected in this function based on whether they should be read or not. 

        Args:
            df_with_sheets (Dataframe): Dataframe with ALL sheets of the excelfile as index, and the type of the sheet as value.

        Raises:
            KeyError: If the index of df_with_sheets does NOT correspond with all the sheetnames in the excelfile.

        Returns:
            List[str]: List of sheets that need to be read.
        """
        ef_sheets = df_with_sheets.get_excel_file().get_pandas_excel_file().sheet_names
        pandas_df_with_sheets = df_with_sheets.get_pandas_dataframe()
        sheet_names_index = pandas_df_with_sheets.index
    
        if (ef_sheets == sheet_names_index).all():
            sheets_to_read = []

            for sheet in sheet_names_index:
                if pandas_df_with_sheets.loc[sheet].iloc[0] != sheet_types.get('dont_read'):
                    sheets_to_read.append(sheet)

            return sheets_to_read
        else:
            raise KeyError(f'The df_with_sheets: {df_with_sheets} does not correspond with the sheetnames in the Excelfile. \
                           To solve: Check that the right dataframe is given as argument, that is a dataframe with all the sheet names of the excel file as index, and the sheet type as value, \
                           OR Check that the input in the excel file is correct, that is that all sheets (and hidden sheets) are inputted in Config_main')

