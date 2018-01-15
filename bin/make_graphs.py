#!/usr/bin/env python3
"""Graph data from database CSV file."""

# Standard imports
import sys
import os
import argparse
from pprint import pprint

# pip3 imports
import yaml


# Try to create a working PYTHONPATH
_BIN_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
_ROOT_DIRECTORY = os.path.abspath(os.path.join(_BIN_DIRECTORY, os.pardir))
if _BIN_DIRECTORY.endswith('/fina/bin') is True:
    sys.path.append(_ROOT_DIRECTORY)
else:
    print(
        'This script is not installed in the "fin400a/bin" directory. '
        'Please fix.')
    sys.exit(2)

# Fina imports
from fina import results
from fina import graph


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

    distance = 200
    gender = 'm'
    stroke = 'medley'
    course = 'lcm'

    # Create database in memory
    plot = graph.Graph(database_file, course=course)
    plot.bmi_kgspeed(stroke, distance, gender)
    plot.bmi_speed(stroke, distance, gender)
    plot.speed_kgspeed(stroke, distance, gender)

    # plot = graph.Graph(database_file, fastest=False, course=course)
    # plot.bmi_kgspeed(stroke, distance, gender)
    # plot.bmi_speed(stroke, distance, gender)

if __name__ == '__main__':
    main()
