#!/usr/bin/env python3
"""Graph data from database CSV file."""

# Standard imports
import sys
import os
import argparse
import csv
import hashlib
from pprint import pprint
from collections import defaultdict

# pip3 imports
import yaml


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


def _read_database(filename):
    """Process the database file.

    Args:
        filename: Database filename

    Returns:
        events: Anonymized dict of best results per athlete keyed by
            hash, stroke, distance and gender

    """
    # Initialize key variables
    athletes = {}
    events = defaultdict(lambda: defaultdict(
        lambda: defaultdict(lambda: defaultdict())))

    # Read CSV file
    with open(filename) as csvfile:
        f_handle = csv.reader(csvfile, delimiter=',')
        for row in f_handle:
            (firstname, lastname, birthyear, gender, stroke,
             distance, _time, data, superkey) = _process_row(row)

            if superkey in athletes:
                athletes[superkey] = max(_time, athletes[superkey])
            else:
                athletes[superkey] = _time

    # Read CSV file again
    with open(filename) as csvfile:
        f_handle = csv.reader(csvfile, delimiter=',')
        for row in f_handle:
            (firstname, lastname, birthyear, gender, stroke,
             distance, _time, data, superkey) = _process_row(row)

            if athletes[superkey] == _time:
                events[superkey][stroke][distance][gender] = data

    return events

def _process_row(row):
    """Process the database row.

    Args:
        row: Database row

    Returns:
        data: tuple of important row data

    """
    firstname = row[9]
    lastname = row[10]
    birthyear = row[11]
    gender = row[8]
    stroke = row[6]
    distance = row[5]
    _time = row[-1]
    _data = {
        'bmi': float(row[14]),
        'speed_per_kg': float(row[15]),
        'speed': float(row[16])}
    superkey = hashlib.sha256(
        bytes('{}{}{}{}{}'.format(
            firstname, lastname, birthyear, stroke, distance),
        'utf-8')).hexdigest()

    data = (
        firstname, lastname, birthyear, gender, stroke,
        distance, _time, _data, superkey)

    return data


def main():
    """Main Function.

    Process Fina XML file

    """
    # Initialize key variables

    # Get filename
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-d', '--database_file',
        help='Name of output file.',
        type=str, required=True)
    args = parser.parse_args()
    database_file = args.database_file

    # Create database in memory
    database = _read_database(database_file)

    pprint(database)
    pprint(len(database))


if __name__ == '__main__':
    main()
