from dataframe import Dataframe

class Dataframe_Reader(Dataframe):
    def __init__(self, file_path:str):
        super().__init__(super().get_name_dataframe, super().get_excel_path_dataframe)
        self.file_path = file_path
    

