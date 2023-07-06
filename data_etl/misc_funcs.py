
def get_data_type(s):
    """
    Function to identify the potential data type of a string. It checks whether the string can be cast to an 
    integer, float, or should remain a string.
    
    Parameters:
    s (str): The string to check

    Returns:
    str: 'int' if the string can be cast to an integer, 'float' if it can be cast to a float, 'str' if it 
    should remain a string.
    """
    try:
        int(s)
        return 'int'
    except ValueError:
        try:
            float(s)
            return 'float'
        except ValueError:
            return 'str'