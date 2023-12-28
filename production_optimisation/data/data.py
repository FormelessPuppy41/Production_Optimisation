import pandas as pd
import openpyxl
from icecream import ic

from general_configuration import dfs

class BaseDataframe:
    def __init__(self, pandas_ExcelFile: pd.ExcelFile, name_Dataframe: str, name_ExcelSheet: str) -> None:
        self.name_dataframe = name_Dataframe
        self.name_ExcelSheet = name_ExcelSheet
        self.pandas_ExcelFile  = pandas_ExcelFile
        self.pandas_Dataframe: (pd.DataFrame, pd.Series) = None

        self.cleaned_Status_Dataframe: bool = False

    ### RETRIEVING INFORMATION ABOUT THE DATAFRAME
    def get_name_Dataframe(self) -> str:
        return self.name_dataframe
    
    def get_name_ExcelSheet(self) -> str:
        return self.name_ExcelSheet
    
    def get_pandas_ExcelFile(self) -> pd.ExcelFile:
        return self.pandas_ExcelFile
    
    def get_pandas_Dataframe(self) -> pd.DataFrame:
        return self.pandas_Dataframe
    
    def get_cleanedStatus(self) -> bool:
        return self.cleaned_Status_Dataframe
    
    def clean():
        pass

    def write_Dataframe_toExcel(self):
        if self.name_ExcelSheet is None:
            raise ValueError('Dataframe does not have its own sheet in the ExcelFile')
        elif self.name_ExcelSheet not in self.pandas_ExcelFile.sheet_names:
            raise ValueError(f'The given sheetname ({self.name_ExcelSheet}) for the dataframe ({self.name_dataframe}) cannot be found in the sheet_names within the given ExcelFile ({self.pandas_ExcelFile})')
        
        elif self.name_ExcelSheet in self.pandas_ExcelFile.sheet_names:
            with pd.ExcelWriter(
                path=self.pandas_ExcelFile.io, mode='a', if_sheet_exists='replace', 
                engine='openpyxl', engine_kwargs={'keep_vba': True}
                ) as writer:
                #FIXME:
                self.pandas_Dataframe.to_excel(excel_writer=writer, sheet_name=self.name_ExcelSheet, index=True)
        
        ic(f'Dataframe ({self.name_dataframe}) written to ExcelFile in sheet ({self.name_ExcelSheet}) correctly.')


class ordersDataframe(BaseDataframe):
    def __init__(self) -> None:
        super().__init__()
    
    def clean():
        pass

class ManagerDataframes:
    def __init__(self) -> None:
        pass