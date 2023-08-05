import pandas as pd

from data import data_helpers
from data.dataframe import Dataframe

class Dataframe_Cleaner:
    """The Dataframe_Cleaner class is for cleaning dataframes.
    """
    def __init__(self, dataframe: Dataframe):
        self.dataframe = dataframe
        self.pandas_df = self.dataframe.get_pandas_dataframe()

    def clean_index_sets_elements(self, element):
        """Cleans the elements in a index list. Only apply this function on index lists. 
        Because if the list has floats with non zero decimals, then those decimals are neglected by the int() function.

        Args:
            element (_type_): Element to be cleaned from index list

        Returns:
            'cleaned element': Either a cleaned element or nothing if the element is None/''
        """
        if element: # Removes Empty / None elements.
            if pd.notna(element) and isinstance(element, str):
                return element.upper()
            elif pd.notna(element) and isinstance(element, pd.Timestamp):
                return element
            elif pd.notna(element) and isinstance(element, float):
                return int(element)
        else:
            return element     


    def clean_orders_elements(self, element, columns):
        if element: 
            if pd.notna(element) and isinstance(element, str) and element.name in columns:
                return element.upper()
        else:
            return element     