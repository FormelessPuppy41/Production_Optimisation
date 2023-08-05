import pandas as pd

def clean_index_set_element(element):
    """Cleans the elements in a index list. Only apply this function on index lists. 
    Because if the list has floats with non zero decimals, then those decimals are neglected by the int() function.

    Args:
        element (_type_): Element to be cleaned from index list

    Returns:
        'cleaned element': Either a cleaned element or nothing if the element is None/''
    """
    if element: # Removes Empty / None elements.
        if isinstance(element, str):
            element = element.upper()
        elif isinstance(element, pd.Timestamp):
            pass
        elif isinstance(element, float):
            element = int(element)
        return element