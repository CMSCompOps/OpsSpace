"""
An example module

:author: Daniel Abercrombie <dabercro@mit.edu>
"""

def example_function(an_integer, a_string, int_or_str):
    """My example function for the developer guidelines.

    :param int an_integer: This is a description for what an integer can be used for
    :param str a_string: This is a description for what a string can be used for
    :param int_or_str: This is just an example for more complex variables types
    :type int_or_str: int or str
    :returns: The number 0
    :rtype: int
    :raises TypeError: If any of the variables are the wrong type
    """

    if not (isinstance(an_integer, int) and isinstance(a_string, str)
            and (isinstance(int_or_str, int) or isinstance(int_or_str, str))):
        raise TypeError('At least one of the input variables is the wrong type.')

    return 0
