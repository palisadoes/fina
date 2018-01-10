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
    data = {}

    # Get filename
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-f', '--filename', help='Name of CSV file to read.',
        type=str, required=True)
    args = parser.parse_args()
    filename = args.filename

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
            data[label] = re.sub('[^0-9]', '', value)
        elif label == 'height':
            data[label] = re.sub('[^0-9]', '', value)
        elif label == 'date of birth':
            data[label] = value

    # Get name
    for div in ['first-name', 'last-name']:
        elements = soup.find_all('div', {'class': div})
        for element in elements:
            data[div] = element.get_text().strip()

    pprint(data)



if __name__ == '__main__':
    main()
