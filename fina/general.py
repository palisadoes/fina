"""Module to process FINA results files."""

# Standard imports
import re


def olympic_name(_name):
    """Method to instantiate the class.

    Args:
        _name: Full name of person

    Returns:
        result: Tuple of (firstname, lastname)

    """
    # Initialize key variables
    result = None

    # Strip nonalpha numeric characters from name
    name = fix_name(_name)

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


def fix_name(_name):
    """Remove all non alphanumeric characters from name.

    Args:
        _name: Full name of person

    Returns:
        result: Stripped name

    """
    # List of characters we don't want to lose
    exceptlist = ' -'

    # Process
    regex = re.compile(r'[^\w{}]'.format(exceptlist))

    # Get rid of excess spaces, strip spaces, strip nonalphanumeric
    words = _name.split()
    name = ' '.join(words)
    result = regex.sub('', name)
    return result
