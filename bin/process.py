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
    # Initialize key variables
    alldata = []

    # Get filename
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-f', '--directory', help='Name of directory with XML files.',
        type=str, required=True)
    args = parser.parse_args()
    directory = args.directory

    # Get a list of files in the directory
    files = os.listdir(directory)
    filenames = ['{}{}{}'.format(
        directory, os.sep, nextfile) for nextfile in files]

    for _filename in sorted(filenames):
        # Get rid of excess os.sep separators
        pathitems = _filename.split(os.sep)
        filename = os.sep.join(pathitems)

        # Skip obvious
        if os.path.isfile(filename) is False:
            continue
        if filename.lower().endswith('.xml') is False:
            continue

        # Get event data
        data = results.File(filename)

        # pprint(data.athletes())
        # pprint(data.results_csv(131))
        meet_results = data.allresults_csv(stage='fin')
        for item in meet_results:
            alldata.append(item)


    pprint(alldata)


if __name__ == '__main__':
    main()
