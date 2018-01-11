#!/usr/bin/env python3
"""Script to process FINA results."""

# Standard imports
import sys
import os
import re
import argparse
from pprint import pprint

# pip3 libraries
from bs4 import BeautifulSoup
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


def main():
    """Main Function.

    Process Fina XML file

    """
    # Initialize key variables
    months = [
        'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul',
        'aug', 'sep', 'oct', 'nov', 'dec']
    profiles = []

    # Get filename
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-f', '--directory', help='Name of directory containing profiles.',
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

        # Initialize profile
        profile = {}

        # Read file
        with open(filename, 'r') as reader:
            html = reader.read()

        # Get div 'biography-element-wrapper'
        soup = BeautifulSoup(html, 'html.parser')

        # Get vitals
        elements = soup.find_all('div', {'class': 'biography-element-wrapper'})
        for element in elements:
            label = element.find(
                'div', {'class': 'label'}).get_text().lower().strip()
            value = element.find('div', {'class': 'value'}).get_text().strip()
            if label == 'weight':
                profile[label] = float(re.sub('[^0-9]', '', value))
            elif label == 'height':
                profile[label] = float(re.sub('[^0-9]', '', value))
            elif label == 'date of birth':
                components = value.split()
                index = months.index(components[1].lower()[:3])
                components[1] = months[index].upper()
                _label = label.replace(' ', '-').lower()
                value = '-'.join(components)
                profile[_label] = value

        # Get name
        for div in ['first-name', 'last-name']:
            elements = soup.find_all('div', {'class': div})
            for element in elements:
                profile[div] = element.get_text().strip()

        # Add to list of profiles
        profiles.append(profile)

    data = yaml.dump({'data': profiles}, default_flow_style=False)
    print(data)


if __name__ == '__main__':
    main()
