#!/usr/bin/env python3
"""Script to process FINA and Olympic athlete profile data.

Data is output to a unified profile YAML file.

"""

# Standard imports
import sys
import os
import re
import argparse
import time
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

# fina imports
from fina import general


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


def _final_athtlete_profiles_html(directory):
    """Function to create list of athlete data from fina.org profiles.

    Args:
        directory: Name of directory containing data

    Returns:
        profiles: List of dicts of data

    """
    # Initialize key variables
    profiles = []

    # Get a list of files in the directory
    files = os.listdir(directory)
    filenames = ['{}{}{}'.format(
        directory.rstrip(os.sep), os.sep, nextfile) for nextfile in files]

    for _filename in sorted(filenames):
        # Get rid of excess os.sep separators
        pathitems = _filename.split(os.sep)
        filename = os.sep.join(pathitems)

        # Skip obvious
        if os.path.isfile(filename) is False:
            continue

        # Print status
        print('Processing file: {}'.format(filename))

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
                profile[div.replace('-', '')] = general.fix_name(
                    element.get_text())

        # We have all the data we have the right
        # most relevant value
        if len(profile.keys()) == 5:
            profile['lastname'] = profile['lastname'].upper()
            profiles.append(profile)

    return profiles


def _listing_xml(directory):
    """Function to create list of athlete data from rio PDF file XML.

    Args:
        directory: Name of directory containing data

    Returns:
        data: List of dicts of data

    """
    # Initialize key variables
    profiles = []
    regex_date = re.compile(r'^.*?>([0-9]+ [A-Z]+ [0-9]+)</text>$')
    regex_height = re.compile(r'^.*?>(\d{1}\.\d{2}) / \d{1}\'\d{1}.*?</text>$')
    regex_weight = re.compile(r'^.*?>(\d{2,3}) / \d{2,3}</text>$')
    regex_offset = re.compile(
        r'^<text .*? left="([0-9]+)" .*?<b>Name</b></text>$')
    regex_combined = re.compile(
        r'^.*?>([0-9]+ [A-Z]+ [0-9]+)\s+(\d{1}\.\d{2})/\d{1}\'\d{1}.*?\s+'
        '(\d{2}\.\d{1})\/.*?</text>$')

    # Get a list of files in the directory
    files = os.listdir(directory)
    filenames = ['{}{}{}'.format(
        directory.rstrip(os.sep), os.sep, nextfile) for nextfile in files]

    for _filename in sorted(filenames):
        # Get rid of excess os.sep separators
        pathitems = _filename.split(os.sep)
        filename = os.sep.join(pathitems)

        # Skip obvious
        if os.path.isfile(filename) is False:
            continue
        if filename.lower().endswith('.xml') is False:
            continue

        # Print status
        print('Processing file: {}'.format(filename))

        # Read file to get the offset where the names will be found. We use
        # the table headings to get this value
        with open(filename, 'r') as reader:
            profile = {}
            for line in reader:
                found = regex_offset.match(line)
                if bool(found) is True:
                    offset = found.group(1)
                    break

        # Read file
        with open(filename, 'r') as reader:
            profile = {}
            for line in reader:
                # Skip headers
                if '<b>' in line:
                    continue

                # Get name
                if ' left="{}" '.format(offset) in line:
                    profile = {}
                    text = _get_text(line)
                    found = general.olympic_name(text)
                    if bool(found) is True:
                        (profile['firstname'], profile['lastname']) = found

                # Check date. The position of this column varies so
                # we have to use a different methodology
                found = regex_date.match(line)
                if bool(found) is True:
                    profile['birthdate'] = _xml_birthdate(found.group(1))

                # height:
                found = regex_height.match(line)
                if bool(found) is True:
                    profile['height'] = float(found.group(1)) * 100

                # weight
                found = regex_weight.match(line)
                if bool(found) is True:
                    profile['weight'] = float(found.group(1))

                    # We have all the data we have the right
                    # most relevant value
                    if len(profile.keys()) == 5:
                        profiles.append(profile)

                # Some files have weight, height and birthdate on the same line
                found = regex_combined.match(line)
                if bool(found) is True:
                    profile['birthdate'] = _xml_birthdate(found.group(1))
                    profile['height'] = float(found.group(2)) * 100
                    profile['weight'] = float(found.group(3))

                    # We have all the data we have the right
                    # most relevant value
                    if len(profile.keys()) == 5:
                        profiles.append(profile)

    data = _dedup(profiles)
    return data


def _xml_birthdate(text):
    """Convert birthdate to standard format.

    Args:
        text: Text to extract height from

    Returns:
        result: YYYY-MM-DD format

    """
    values = text.split()
    day = values[0].zfill(2)
    month = _month_number(values[1])
    year = values[2]
    result = '-'.join([year, month, day])
    return result


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
    ts_start = int(time.time())

    # Get CLI arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-f', '--fina_directory',
        help='Name of directory containing FINA athlete profiles.',
        type=str, required=True)
    parser.add_argument(
        '-l', '--listing_directory',
        help='Name of directory containing Rio2016 athlete profiles.',
        type=str, required=True)
    parser.add_argument(
        '-p', '--profile_directory',
        help='Name of directory in which combined profiles will be stored.',
        type=str, required=True)
    args = parser.parse_args()
    fina_directory = args.fina_directory
    listing_directory = args.listing_directory
    profile_directory = args.profile_directory

    # Get profiles
    profiles.extend(_listing_xml(listing_directory))

    # Get more profiles
    profiles.extend(_final_athtlete_profiles_html(fina_directory))
    uniques = _dedup(profiles)

    data = yaml.dump({'data': uniques}, default_flow_style=False)
    with open('{}/athletes.yaml'.format(profile_directory), 'w') as writer:
        writer.write(data)

    # Describe success
    print('Athlete profiles processed: {}'.format(len(uniques)))
    print('Duration: {}'.format(int(time.time() - ts_start)))


if __name__ == '__main__':
    main()
