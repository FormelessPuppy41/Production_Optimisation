import pandas as pd
import contextlib

from data.dataframe import Dataframe
from general_configuration import description_order_df, sheet_types

class Data_Cleaner:
    """The Data_Cleaner class enables the user to clean dataframes. 
    There are 'helper' function which can be combined to create a function to clean a single dataframe.
    """
    
    def __init__(self, dataframe: Dataframe):
        """Constructor for the data_cleaner class.

        Args:
            dataframe (Dataframe): Dataframe to clean.
        """
        self.dataframe = dataframe
        self.pandas_df = self.dataframe.get_pandas_dataframe()


    # Main function that cleans the different types of dataframes
    def clean_dfs(self, df_helper_read_sheets: Dataframe): 
        #FIXME: indexsets/Uppercase in columns, It might be usefull to add a cleaner that changes columns and indices to upper \
        # if they have the label where they have index sets in the df. but this is easier to check whether all the inputted \
        # values in the indexsetdf is uppercase, being both here and in excel everything comes from that df or the ordersdf
        """Applies a cleaning process based on the type of the dataframe.
        """
        if not self.dataframe.get_cleaned_status():
            try:
                sheet_type = df_helper_read_sheets.get_pandas_dataframe().loc[self.dataframe.excel_sheet_name].iloc[0]
            except:
                sheet_type = None
                print(f'{self.dataframe.get_pandas_dataframe} cannot find a excel_sheet_name')
                pass
            if sheet_type == sheet_types.get('index_in_col_A'):
                self.change_df_index_to_one()
            elif sheet_type == sheet_types.get('orders'):
                self.clean_order_df()
                self.change_df_index_to_one()
            elif sheet_type == sheet_types.get('index_sets'):
                self.clean_index_sets_df()



    # Clean functions for the actual dataframes.
    def clean_helper_read_sheets_df(self):
        """Function to clean the helper_read_sheets dataframe.
        """
        if not self.dataframe.get_cleaned_status():
            self.change_df_index_to_one()
            self.dataframe.change_status_to_cleaned()


    def clean_index_sets_df(self):
        """Function to clean the index_sets_dataframe
        """
        if not self.dataframe.get_cleaned_status():
            self.pandas_df = self.pandas_df.applymap(self.clean_index_sets_elements)
    
            self.dataframe.change_pandas_dataframe(self.pandas_df)
            self.dataframe.change_status_to_cleaned()

        
    def clean_order_df(self):
        """Function to clean the Orders_df
        """
        if not self.dataframe.get_cleaned_status():
            self.columns_to_clean = self.pandas_df.columns.drop(description_order_df)

            for col in self.pandas_df.columns:
                self.pandas_df[col] = self.pandas_df[col].apply(lambda x: self.clean_orders_elements(x, col))
            
            self.dataframe.change_pandas_dataframe(self.pandas_df)
            self.dataframe.change_status_to_cleaned()



    # Helper functions for cleaning:
    def clean_index_sets_elements(self, element):
        """Cleans the elements in a index list. Only apply this function on index lists. 
        Because if the list has floats with non zero decimals, then those decimals are neglected by the int() function.

        Args:
            element (_type_): Element to be cleaned from index list

        Returns:
            'cleaned element': Either a cleaned element or the old element''
        """
        #FIXME: index_sets: Instead of only changing them, should this not also give like a warning message that indicates which values are wrong. \
        #  because then the other dataframes with these as indices/columns don't need to be cleaned for those things.
        if element: # Removes Empty / None elements.
            if pd.notna(element) and isinstance(element, str):
                return element.upper()
            elif pd.notna(element) and isinstance(element, pd.Timestamp):
                return element
            elif pd.notna(element) and isinstance(element, float):
                return int(element)
        else:
            return element


    def clean_orders_elements(self, element, column_name):
        """Cleans the elements of the orders_df per column. Only apply this function on the orders_df.
        Otherwise datapoint might change. 

        Args:
            element (_type_): Element to be cleaned in orders_df
            column_name (_type_): Column of orders_df that must be cleaned.

        Returns:
            'cleaned element': Either a cleaned element or the old element
        """
        if element: 
            if pd.notna(element) and isinstance(element, str) and column_name in self.columns_to_clean:
                return element.upper()
            else:
                return element
        else:
            return element         
        
    
    def change_df_index_to_one(self):
        """Changes the index of a dataframe to the first column.
        """
        
        if not self.pandas_df.empty:
            columns = self.pandas_df.columns
            self.pandas_df = self.pandas_df.set_index(columns[0])

            self.dataframe.change_pandas_dataframe(self.pandas_df)