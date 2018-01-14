#!/usr/bin/env python3
"""Script to process FINA and Olympic results.

The final data is stored in a database CSV file.

"""

# Standard imports
import sys
import os
import argparse
import csv
import re
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


def _read_profiles(profile_directory):
    """Function to read profile files.

    Args:
        directory: Name of directory containing data

    Returns:
        profiles: Dict of profiles keyed by lastname, firstname

    """
    # Initialize key variables
    profiles = defaultdict(
        lambda: defaultdict(lambda: defaultdict()))

    # Read the yaml files in the profiles directory
    files = os.listdir(profile_directory)
    filenames = ['{}{}{}'.format(
        profile_directory, os.sep, nextfile) for nextfile in files]

    for _filename in sorted(filenames):
        # Get rid of excess os.sep separators
        pathitems = _filename.split(os.sep)
        filename = os.sep.join(pathitems)

        # Skip obvious
        if os.path.isfile(filename) is False:
            continue
        if filename.lower().endswith('.yaml') is False:
            continue

        with open(filename, 'r') as stream:
            try:
                _profiles = yaml.load(stream)['data']
            except yaml.YAMLError as exc:
                print(exc)

    # Create dictionary
    for item in _profiles:
        firstname = item['firstname']
        lastname = item['lastname']
        height = item['height']
        weight = item['weight']
        birthdate = item['birthdate']
        profiles[lastname][firstname][birthdate] = {
            'height': height, 'weight': weight}

    return profiles


def _fina(fina_directory, profiles):
    """Process Fina result files.

    Args:
        fina_directory: Name of directory containing data
        profiles: Dict of swimmer profiles for height / weight lookup

    Returns:
        alldata: List of list of data

    """
    # Initialize key variables
    alldata = []
    data_directories = []
    regex = re.compile(r'^.*?(\/\d{4})$')

    # Recursively get filenames under directory
    for root, subdirectories, _ in os.walk(fina_directory):
        for subdirectory in subdirectories:
            path = '{}{}{}'.format(root, os.sep, subdirectory)
            found = regex.match(path)
            if bool(found) is True:
                data_directories.append(path)

    for data_directory in data_directories:
        # Get a list of files in the meet directory
        files = os.listdir(data_directory)
        filenames = ['{}{}{}'.format(
            data_directory, os.sep, nextfile) for nextfile in files]

        for _filename in sorted(filenames):
            # Get rid of excess os.sep separators
            pathitems = _filename.split(os.sep)
            filename = os.sep.join(pathitems)

            # Skip obvious
            if os.path.isfile(filename) is False:
                continue
            if filename.lower().endswith('.xml') is False:
                continue

            # Print progress
            print('Processing file: {}'.format(filename))

            # Get event data
            data = results.FileFina(filename, profiles)

            # Get XML filenames
            meet_results = data.allresults_csv(stage=None)
            for item in meet_results:
                alldata.append(item)

    return alldata


def _olympic(olympic_directory, profiles):
    """Process Fina result files.

    Args:
        olympic_directory: Name of directory containing data
        profiles: Dict of swimmer profiles for height / weight lookup

    Returns:
        alldata: List of list of data

    """
    # Initialize key variables
    alldata = []

    # Get a list of files in the meet directory
    files = os.listdir(olympic_directory)
    filenames = ['{}{}{}'.format(
        olympic_directory, os.sep, nextfile) for nextfile in files]

    for _filename in sorted(filenames):
        # Get rid of excess os.sep separators
        pathitems = _filename.split(os.sep)
        filename = os.sep.join(pathitems)

        # Skip obvious
        if os.path.isfile(filename) is False:
            continue
        if filename.lower().endswith('.xlsx') is False:
            continue

        # Print progress
        print('Processing file: {}'.format(filename))

        # Get event data
        data = results.FileOlympics2016(filename, profiles)

        meet_results = data.allresults_csv(stage=None)
        for item in meet_results:
            alldata.append(item)

    return alldata


def main():
    """Main Function.

    Process Fina XML file

    """
    # Initialize key variables
    alldata = []
    finadata = []
    olympicdata = []

    # Get filename
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-f', '--fina_directory',
        help='Name of directory with FINA XML files.',
        type=str, required=True)
    parser.add_argument(
        '-o', '--olympic_directory',
        help='Name of directory with Olympic XLSX files.',
        type=str, required=True)
    parser.add_argument(
        '-p', '--profile_directory',
        help='Name of directory with athlete profiles.',
        type=str, required=True)
    parser.add_argument(
        '-d', '--database_file',
        help='Name of database file.',
        type=str, required=True)
    args = parser.parse_args()
    fina_directory = args.fina_directory
    profile_directory = args.profile_directory
    database_file = args.database_file
    olympic_directory = args.olympic_directory

    # Get the profiles
    profiles = _read_profiles(profile_directory)

    # Process Fina data
    finadata = _fina(fina_directory, profiles)

    # Process Olympic data
    olympicdata = _olympic(olympic_directory, profiles)

    # Get all data
    alldata.extend(finadata)
    alldata.extend(olympicdata)

    # Create output file
    with open(database_file, 'w') as f_handle:
        writer = csv.writer(f_handle, delimiter='|')
        writer.writerows(alldata)

    # Print status
    print('{} swimmer event results created'.format(len(alldata)))


if __name__ == '__main__':
    main()