#!/usr/bin/env python3
"""Script to process FINA results."""

# Standard imports
import sys
import os
import argparse
import csv
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


def main():
    """Main Function.

    Process Fina XML file

    """
    # Initialize key variables
    alldata = []

    # Get filename
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-m', '--meet_directory', help='Name of directory with XML files.',
        type=str, required=True)
    parser.add_argument(
        '-p', '--profile_directory',
        help='Name of directory with athlete profiles.',
        type=str, required=True)
    parser.add_argument(
        '-o', '--output_file',
        help='Name of output file.',
        type=str, required=True)
    args = parser.parse_args()
    meet_directory = args.meet_directory
    profile_directory = args.profile_directory
    output_file = args.output_file

    # Get the profiles
    profiles = _read_profiles(profile_directory)

    # Get a list of files in the meet directory
    files = os.listdir(meet_directory)
    filenames = ['{}{}{}'.format(
        meet_directory, os.sep, nextfile) for nextfile in files]

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
        data = results.File(filename, profiles)

        # pprint(data.athletes())
        # pprint(data.results_csv(131))
        meet_results = data.allresults_csv(stage=None)
        for item in meet_results:
            alldata.append(item)

    pprint(alldata)
    print('\n', len(alldata))

    # Create output file
    with open(output_file, 'w') as f_handle:
        writer = csv.writer(f_handle)
        writer.writerows(alldata)


if __name__ == '__main__':
    main()
