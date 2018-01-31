#!/usr/bin/env python3
"""Graph data from database CSV file."""

# Standard imports
import sys
import os
import argparse
import csv
from pprint import pprint
import pathos.multiprocessing as multiprocessing

# pip3 imports

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
from fina import log


def main():
    """Main Function.

    Process Fina XML file

    """
    # Parse the CLI
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='action')

    # 'save' Parameter
    save = subparsers.add_parser('save')
    save.add_argument(
        '-d', '--database_file',
        help='Name of output file.',
        type=str, required=True)
    save.add_argument(
        '-o', '--output_directory',
        help='Directory where all graphs will be created.',
        type=str, required=True)

    # 'display' Parameter
    display = subparsers.add_parser(
        'display', help='Display chart on your desktop')
    display.add_argument(
        '-d', '--database_file',
        help='Name of output file.',
        type=str, required=True)
    display.add_argument(
        '-l', '--distance',
        choices=[
            100, 1500, 1508.76, 182.88, 200, 365.76,
            400, 45.72, 457.2, 50, 800, 91.44],
        help='Event distance.',
        type=float, required=True)
    display.add_argument(
        '-g', '--gender',
        help='Gender of event participants.',
        choices=['m', 'f', 'male', 'female', 'women', 'both', 'None', 'none'],
        type=str, required=True)
    display.add_argument(
        '-s', '--stroke',
        choices=['free', 'breast', 'back', 'fly', 'butterfly', 'medley'],
        help='Event stroke.',
        type=str, required=True)
    display.add_argument(
        '-c', '--course',
        choices=['lcm', 'scm', 'scy', 'LCM', 'SCM', 'SCY'],
        help='Event stroke.',
        type=str, required=True)

    # Parse the arguments
    args = parser.parse_args()

    # Do next best thing
    if args.action == 'save':
        _save_graph(args)
    elif args.action == 'display':
        _display_graph(args)
    else:
        args.print_help()
    sys.exit(0)


def _save_graph(args):
    """Display the relevant chart.

    Args:
        args: CLI arguments object

    Returns:
        None

    """
    # Initialize key variables
    delimiter = '|'
    data = {}
    genders = ['M', 'F', 'B', None]
    database_file = args.database_file
    output_directory = args.output_directory
    arguments = []

    # Make sure files and directories exist
    if os.path.isfile(database_file) is False:
        log_message = (
            'Database file {} does not exist'.format(database_file))
        log.log2die(1005, log_message)
    elif os.path.isdir(output_directory) is False:
        log_message = (
            'Output directory {} does not exist'.format(output_directory))
        log.log2die(1005, log_message)

    # Get the parameters to be used to create graphs
    header = True
    with open(database_file) as csvfile:
        f_handle = csv.reader(csvfile, delimiter=delimiter)
        for row in f_handle:
            # Skip the header
            if header is True:
                header = False
                continue

            # Create information
            course = row[3]
            distance = row[5]
            stroke = row[6]
            data['{} {} {}'.format(course, stroke, distance)] = None

    # Cycle through data
    for gender in genders:
        for value in sorted(data.keys()):
            [course, stroke, distance] = value.split()
            arguments.append((
                database_file, output_directory, distance,
                stroke, course, gender))

    # Create subprocesses to do the job
    processes = multiprocessing.cpu_count() - 1
    with multiprocessing.Pool(processes=processes) as pool:
        pool.starmap(_save_graph_subprocess, arguments)

    # Print status
    print('Done.')


def _save_graph_subprocess(
        database_file, output_directory, distance, stroke, course, gender):
    """Display the relevant chart.

    Args:
        database_file: Database file Name
        output_directory: Directory where images will be saved
        distance: Event distance
        stroke: Event stroke
        course: Course
        gender: Gender of participants

    Returns:
        None

    """
    graphfile = (
        '{}m-{}-{}-{}'.format(
            distance, stroke, course, gender))
    _filename = (
        '{}{}{}').format(
            output_directory.rstrip(os.sep), os.sep, graphfile)

    # Print status
    print(
        'Creating chart for {}m, stroke {}, course {}, gender {} '
        'as file: {}'
        ''.format(distance, stroke, course, gender, _filename))

    # Create graph file
    plot = graph.Graph(
        database_file, course=course)
    plot.bmi_kgspeed(
        stroke, distance, gender=gender,
        filename=('{}-bmi-kgspeed.png'.format(_filename)))
    plot.bmi_speed(
        stroke, distance, gender=gender,
        filename=('{}-bmi-speed.png'.format(_filename)))
    plot.speed_kgspeed(
        stroke, distance, gender=gender,
        filename=('{}-speed-kgspeed.png'.format(_filename)))


def _display_graph(args):
    """Display the relevant chart.

    Args:
        args: CLI arguments object

    Returns:
        None

    """
    # Initialize key variables
    database_file = args.database_file
    distance = args.distance
    stroke = args.stroke
    course = args.course
    _gender = args.gender

    # Reassign gender variable
    if _gender.lower() == 'none':
        gender = None
    else:
        gender = _gender

    # Create database in memory
    plot = graph.Graph(database_file, course=course)
    plot.bmi_speed(stroke, distance, gender)
    plot.bmi_sqrt_speed(stroke, distance, gender)
    plot.bmi_sq_speed(stroke, distance, gender)
    plot.bmi_kgspeed(stroke, distance, gender)
    plot.speed_kgspeed(stroke, distance, gender)


if __name__ == '__main__':
    main()
