"""Module to process FINA results files."""

# Standard imports
import re


def olympic_name(name):
    """Method to instantiate the class.

    Args:
        name: Full name of person

    Returns:
        result: Tuple of (firstname, lastname)

    """
    # Initialize key variables
    result = None
    
    # regex_name = re.compile(r'^([A-Z\-]+)\s+(.*?)$')
    regex_name = re.compile(r'^([A-Z\-\']+)$')

    # Names are usually of the format:
    #   LASTNAME Firstname
    #   LAST NAME Firstname
    #   LAST-NAME Firstname
    #   O'LASTNAME Firstname
    #   McLASTNAME Firstname
    # This logic fixes all instances of this
    components = name.split()
    for index in range(len(components) - 1, -1, -1):
        # Some names have asterisks after them
        found = regex_name.match(components[
            index].replace('*', '').replace('Mc', 'MC'))
        if bool(found) is True:
            lastname = ' '.join(components[0:index + 1]).upper()
            firstname = ' '.join(components[index + 1:])
            result = (firstname, lastname)
            break

    # Return
    return result
