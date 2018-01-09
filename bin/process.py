#!/usr/bin/env python3
"""Script to process FINA results."""

# Standard imports
import sys
import os
import argparse
from pprint import pprint


# Try to create a working PYTHONPATH
_BIN_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
_ROOT_DIRECTORY = os.path.abspath(os.path.join(_BIN_DIRECTORY, os.pardir))
if _BIN_DIRECTORY.endswith('/fina/bin') is True:
    sys.path.append(_ROOT_DIRECTORY)
else:
    print(
        'This script is not installed in the "fina/bin" directory. '
        'Please fix.')
    sys.exit(2)

# Fina imports
from fina import results


def main():
    """Main Function.

    Process Fina XML file

    """
    # Get filename
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-f', '--filename', help='Name of CSV file to read.',
        type=str, required=True)
    args = parser.parse_args()
    filename = args.filename

    # Get event data
    data = results.File(filename)
    '''sessions = data.sessions()
    for session in sessions:
        session_id = session['number']
        print('\n')
        pprint(data.events(session_id))'''

    clubs = data.clubs()
    for club in clubs:
        club_id = club['code']
        print('\n')
        pprint(data.athletes(club_id))
        break


if __name__ == '__main__':
    main()
