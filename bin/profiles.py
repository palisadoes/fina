#!/usr/bin/env python3
"""Script to process FINA results."""

# Standard imports
import sys
import os
import re
import argparse
from pprint import pprint
from collections import defaultdict

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


def _month_number(month):
    """Function to return the month number based on the month name.

    Args:
        month: Name of month

    Returns:
        result: Month number

    """
    # Initialize key variables
    months = {
        'jan': 1,
        'feb': 2,
        'mar': 3,
        'apr': 4,
        'may': 5,
        'jun': 6,
        'jul': 7,
        'aug': 8,
        'sep': 9,
        'oct': 10,
        'nov': 11,
        'dec': 12}
    key = month[0:3].lower()
    result = str(months[key]).zfill(2)
    return result


def _fina_html(directory):
    """Function to create list of athlete data from fina.org profiles.

    Args:
        directory: Name of directory containing data

    Returns:
        profiles: List of dicts of data

    """
    # Initialize key variables
    months = [
        'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul',
        'aug', 'sep', 'oct', 'nov', 'dec']
    profiles = []

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
                day = components[0].zfill(2)
                month = _month_number(components[1])
                year = components[2]
                value = '-'.join([year, month, day])
                profile['birthdate'] = value

        # Get name
        for div in ['first-name', 'last-name']:
            elements = soup.find_all('div', {'class': div})
            for element in elements:
                profile[div.replace('-', '')] = element.get_text().strip()

        # We have all the data we have the right
        # most relevant value
        if len(profile.keys()) == 5:
            profile['lastname'] = profile['lastname'].upper()
            profiles.append(profile)

    return profiles


def _rio_xml(directory):
    """Function to create list of athlete data from rio PDF file XML.

    Args:
        directory: Name of directory containing data

    Returns:
        data: List of dicts of data

    """
    # Initialize key variables
    profiles = []
    regex_name = re.compile(r'^([A-Z]+)\s+(.*?)$')
    regex_date = re.compile(r'^.*?>([0-9]+ [A-Z]+ [0-9]+)</text>$')

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

        # Read file
        with open(filename, 'r') as reader:
            profile = {}
            for line in reader:
                # Skip headers
                if '<b>' in line:
                    continue

                # Check date. The position of this column varies so
                # we have to use a different methodology
                found = regex_date.match(line)
                if bool(found) is True:
                    text = _get_text(line)
                    values = text.split()
                    day = values[0].zfill(2)
                    month = _month_number(values[1])
                    year = values[2]
                    value = '-'.join([year, month, day])
                    profile['birthdate'] = value

                # Get name
                if ' left="395" ' in line:
                    profile = {}
                    text = _get_text(line)
                    found = regex_name.match(text)
                    if bool(found) is True:
                        # Some names have asterisks after them
                        lastname = found.group(1).replace('*', '')
                        firstname = found.group(2).replace('*', '')
                        profile['firstname'] = firstname
                        profile['lastname'] = lastname.upper()

                # height:
                elif ' left="655" ' in line:
                    text = _get_text(line)
                    value = float(text.split()[0]) * 100
                    profile['height'] = value

                # weight
                elif ' left="727" ' in line:
                    text = _get_text(line)
                    _value = float(text.split()[0])
                    profile['weight'] = _value

                    # We have all the data we have the right
                    # most relevant value
                    if len(profile.keys()) == 5:
                        profiles.append(profile)

    data = _dedup(profiles)
    return data


def _dedup(profiles):
    """Remove any duplicates in profile list.

    Args:
        profiles: List of profiles

    Returns:
        data: Deduplicated profiles list

    """
    # Initialize key variables
    results = defaultdict(lambda: defaultdict(lambda: defaultdict()))
    data = []

    # Get rid of any duplicates from the profiles list of dicts
    for item in profiles:
        firstname = item['firstname']
        lastname = item['lastname']
        height = item['height']
        weight = item['weight']
        dob = item['birthdate']
        results[lastname][firstname][dob] = [height, weight]

    for lastname in sorted(results.keys()):
        for firstname in sorted(results[lastname].keys()):
            for dob in sorted(results[lastname][firstname].keys()):
                _profile = {}
                _profile['firstname'] = firstname
                _profile['lastname'] = lastname
                [height, weight] = results[lastname][firstname][dob]
                _profile['height'] = height
                _profile['weight'] = weight
                _profile['birthdate'] = dob
                data.append(_profile)

    return data


def _get_text(line):
    """Get value in text element of XML.

    Args:
        line: line of XML

    Returns:
        text: Text string

    """
    # Go!
    elements = line.split('>')
    data = elements[1].split('<')
    text = data[0]
    return text


def main():
    """Main Function.

    Process Fina XML file

    """
    # Initialize key variables
    profiles = []

    # Get CLI arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-p', '--profile_directory',
        help='Name of directory containing profiles.',
        type=str, required=True)
    parser.add_argument(
        '-r', '--rio_directory',
        help='Name of directory containing Rio2016 profiles.',
        type=str, required=True)
    parser.add_argument(
        '-o', '--output_directory',
        help='Name of directory containing the final output.',
        type=str, required=True)
    args = parser.parse_args()
    profile_directory = args.profile_directory
    rio_directory = args.rio_directory
    output_directory = args.output_directory

    # Get profiles
    profiles.extend(_fina_html(profile_directory))
    profiles.extend(_rio_xml(rio_directory))
    uniques = _dedup(profiles)

    data = yaml.dump({'data': uniques}, default_flow_style=False)
    with open('{}/athletes.yaml'.format(output_directory), 'w') as writer:
        writer.write(data)


if __name__ == '__main__':
    main()
