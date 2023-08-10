


class Data:
    def __init__(self, path_to_data: str):
        self._path_to_data = path_to_data

    def read_sheet(self, contains_helper_reader: bool):
        if contains_helper_reader:
            # read helper df and use to loop through reading others. 
            pass
        else:
            # read sheet and store. 
            pass