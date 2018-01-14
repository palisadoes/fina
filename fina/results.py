"""Module to process FINA and Olympics results files."""

# Standard imports
import xml.etree.ElementTree as ET
import operator
import xlrd
import sys
from pprint import pprint

# Fina imports
from fina import log
from fina import general


class FileOlympics2016(object):
    """Process XLSX Olympics data."""

    def __init__(self, filename, profiles, with_na=False):
        """Method to instantiate the class.

        Args:
            filename: Name of file to process
            profiles: dict of athlete profiles
            with_na: Include swimmers where there are N/A values for
                weight or height

        Returns:
            None

        """
        # Initialize key variables
        self._results = []

        # Start handling the workbook
        xl_workbook = xlrd.open_workbook(filename)
        xl_sheet = xl_workbook.sheet_by_index(0)

        # Get row data
        _num_cols = xl_sheet.ncols

        # Get header information
        header = []
        for col_idx in range(0, _num_cols):
            value = xl_sheet.cell_value(0, col_idx)
            if bool(value) is True:
                header.append(value)
        num_cols = len(header)

        # Get row data
        for row_idx in range(1, xl_sheet.nrows):
            row = []
            # Read each column
            for col_idx in range(0, num_cols):
                cell_value = str(xl_sheet.cell_value(row_idx, col_idx)).strip()

                # Calculate time in seconds
                if col_idx != num_cols - 1:
                    row.append(cell_value)
                else:
                    components = cell_value.split(':')
                    if len(components) == 1:
                        row.append(cell_value)
                        row.append(cell_value)
                    else:
                        minutes = float(components[0])
                        seconds = float(components[1])
                        swimtime = round((minutes * 60) + seconds, 3)
                        row.append(cell_value)
                        row.append(str(swimtime))

            # Convert all row items to string
            for index, value in enumerate(row):
                row[index] = str(value)

            # Create participant information
            paricipant = {}
            paricipant['city'] = 'Rio de Janeiro'
            paricipant['nation'] = 'BRA'
            paricipant['course'] = 'LCM'
            paricipant['meet'] = '2016 Olympics'
            paricipant['event'] = row[0]
            paricipant['round'] = row[1]
            paricipant['stroke'] = row[2]
            paricipant['event_id'] = str(int(float(row[3])))
            paricipant['distance'] = str(int(float(row[4])))
            paricipant['gender'] = row[5]
            paricipant['rank'] = str(int(float(row[6])))
            paricipant['heat'] = row[7]

            try:
                paricipant['lane'] = str(int(float(row[8])))
            except:
                paricipant['lane'] = row[8]

            (paricipant['firstname'],
             paricipant['lastname']) = general.olympic_name(row[9])

            try:
                paricipant['birthyear'] = str(int(float(row[10])))
            except:
                paricipant['birthyear'] = row[10]

            paricipant['nation'] = row[11]
            paricipant['swimtime'] = row[12]
            paricipant['time'] = float(row[13])
            self._results.append(paricipant)

        self._profiles = profiles
        self._with_na = with_na

    def events(self, stage=None):
        """Get all event information.

        Args:
            stage: Round of event


        Returns:
            data: List of dicts with information

        """
        pass

    def event(self, event_id):
        """Get event information.

        Args:
            session_id: Session ID number
            event_id: Event ID number

        Returns:
            data: dict with information. None if not found

        """
        # Get data
        pass

    def athletes(self):
        """Get all athlete information.

        Args:
            None

        Returns:
            data: List of dicts with information

        """
        # Get data
        pass

    def athlete(self, athlete_id):
        """Get athlete information.

        Args:
            athlete_id: Athlete ID number

        Returns:
            data: dict with information. None if not found

        """
        # Get data
        pass

    def results(self, event_id):
        """Get results for an event.

        Args:
            event_id: Event ID number

        Returns:
            data: List of dicts with information

        """
        # Initialize key variables
        pass

    def results_csv(self):
        """Get results for an event.

        Args:
            None

        Returns:
            data: List of dicts with information

        """
        # Initialize key variables
        data = []
        factor = 6

        # Get data for participants
        for participant in self._results:
            firstname = participant['firstname']
            lastname = participant['lastname']
            gender = participant['gender']
            birthyear = participant['birthyear']
            swimtime = participant['time']
            stroke = participant['stroke']
            distance = participant['distance']
            city = participant['city']
            nation = participant['nation']
            meet = participant['meet']
            course = participant['course']
            event_id = participant['event_id']
            _round = participant['round']

            # Don't process people with zero times
            if bool(swimtime) is False:
                continue

            # Get height and weight data
            values = self._height_weight(firstname, lastname)
            if bool(values) is False:
                if self._with_na is True:
                    bmi = 'N/A'
                    speed = 'N/A'
                    speed_per_kg = 'N/A'
                    weight = 'N/A'
                    height = 'N/A'
                else:
                    continue
            else:
                (height, weight) = values

                _bmi = weight / ((height / 100) * (height / 100))
                bmi = str(round(_bmi, factor))

                _speed = float(distance) / float(swimtime)
                speed = str(round(_speed, factor))

                _speed_per_kg = _speed / weight
                speed_per_kg = str(round(_speed_per_kg, factor))

            # Create list for output ignoring None values it may contain
            output = [
                meet, city, nation, course,
                event_id, distance, stroke, _round,
                gender, firstname, lastname, birthyear,
                str(height), str(weight),
                bmi,
                speed_per_kg,
                speed,
                swimtime]
            if None in output:
                continue
            data.append(output)

        return data

    def allresults(self, stage=None):
        """Get results for all events.

        Args:
            stage: Round of event

        Returns:
            data: List of dicts with information

        """
        pass

    def allresults_csv(self, stage=None):
        """Get results for all events.

        Args:
            stage: Round of event

        Returns:
            data: List of lists with information

        """
        # Initialize key variables
        _data = []

        # Get results
        result = self.results_csv()
        _data.extend(result)

        data = results_csv_sorter(_data)
        return data

    def _height_weight(self, firstname, lastname):
        """Get weight and height of athlete.

        Args:
            firstname: Athlete first name
            lastname: Athlete last name

        Returns:
            data: tuple of (height, weight)

        """
        # Initialize key variables
        data = None
        profiles = self._profiles

        # Get data
        if lastname in profiles:
            if firstname in profiles[lastname]:
                # Just get the first match
                for birthdate in sorted(profiles[lastname][firstname].keys()):
                    values = profiles[lastname][firstname][birthdate]
                    height = values['height']
                    weight = values['weight']
                    data = (height, weight)
                    break

        return data


class FileFina(object):
    """Process XML data from http://www.omegatiming.com."""

    def __init__(self, filename, profiles, with_na=False):
        """Method to instantiate the class.

        Args:
            filename: Name of file to process
            profiles: dict of athlete profiles
            with_na: Include swimmers where there are N/A values for
                weight or height

        Returns:
            None

        """
        self._root = ET.parse(filename)
        self._profiles = profiles
        self._with_na = with_na

        # Verify the file version is correct
        for node in self._root.iter('LENEX'):
            if 'version' not in node.attrib:
                log_message = (
                    'This file {} is not supported.'.format(filename))
                log.log2die(1000, log_message)
            else:
                if node.attrib['version'] not in ['3.0', '2.0']:
                    log_message = (
                        'This version of file {} is not supported.'
                        ''.format(filename))
                    log.log2die(1001, log_message)

    def meet(self):
        """Get meet information.

        Args:
            None

        Returns:
            data: List of dicts with information

        """
        # Get data
        data = []
        for node in self._root.findall('./MEETS/MEET'):
            data = [node.attrib]
            break
        return data

    def metric(self):
        """Get meet information.

        Args:
            None

        Returns:
            result: True if this is a metric meet

        """
        # Get data
        data = self.meet()[0]
        course = data['course']
        if course[-1].upper() == 'Y':
            result = False
        else:
            result = True
        return result

    def sessions(self):
        """Get session information.

        Args:
            None

        Returns:
            data: List of dicts with information

        """
        # Get data
        data = []
        for node in self._root.findall('./MEETS/MEET/SESSIONS/SESSION'):
            data.append(node.attrib)
        return data

    def events(self, stage=None):
        """Get all event information.

        Args:
            stage: Round of event


        Returns:
            data: List of dicts with information

        """
        # Get data
        data = []

        # Get sesssions
        sessions = self.sessions()
        for session in sessions:
            session_id = session['number']

            # Get event data
            for event in self._root.findall(
                    './MEETS/MEET/SESSIONS/SESSION[@number="{}"]/EVENTS/EVENT'
                    ''.format(session_id)):
                # Store event attributes
                event_id = event.attrib['eventid']
                item = {}
                item['sessionid'] = session_id
                for key, value in event.attrib.items():
                    item[key] = value.strip()

                # Skip rounds depending on 'stage' filter
                if stage is None:
                    pass
                else:
                    if item['round'].upper() != stage.upper():
                        continue

                # Store swimstyle attributes for the event
                for swimstyle in self._root.findall(
                        './MEETS/MEET/SESSIONS/SESSION/EVENTS/EVENT'
                        '[@eventid="{}"]/SWIMSTYLE'.format(event_id)):
                    for key, value in swimstyle.attrib.items():
                        item[key] = value.strip()

                # Modify distance to metric equivalent
                if self.metric() is False:
                    item['distance'] = str(float(item['distance']) * 0.9144)

                # Update data
                data.append(item)

        return data

    def event(self, event_id):
        """Get event information.

        Args:
            session_id: Session ID number
            event_id: Event ID number

        Returns:
            data: dict with information. None if not found

        """
        # Get data
        data = None
        for event in self.events():
            if int(event_id) == int(event['eventid']):
                data = event
        return data

    def clubs(self):
        """Get club information.

        Args:
            None

        Returns:
            data: List of dicts with information

        """
        # Get data
        data = []
        for node in self._root.findall('./MEETS/MEET/CLUBS/CLUB'):
            data.append(node.attrib)
        return data

    def athletes(self):
        """Get all athlete information.

        Args:
            None

        Returns:
            data: List of dicts with information

        """
        # Get data
        data = []

        clubs = self.clubs()
        for club in clubs:
            club_id = club['code']

            # Get athlete data
            for athlete in self._root.findall(
                    './MEETS/MEET/CLUBS/CLUB[@code="{}"]/ATHLETES/ATHLETE'
                    ''.format(club_id)):
                # Store athlete attributes
                athlete_id = athlete.attrib['athleteid']
                item = {}

                # Store vitals for athtlete
                vitals = {}
                vitals['clubid'] = club_id
                for key, value in athlete.attrib.items():
                    vitals[key] = value.strip()
                item['vitals'] = vitals

                # Store entry attributes for the athlete
                entries = self._athlete_entries(club_id, athlete_id)
                item['entries'] = entries

                # Store result attributes for the athlete
                results = self._athlete_results(club_id, athlete_id)
                item['results'] = results

                data.append(item)

        return data

    def _athlete_entries(self, club_id, athlete_id):
        """Get all athlete information.

        Args:
            club_id: Club ID number
            athlete_id: Athlete ID

        Returns:
            data: List of dicts with information

        """
        # Get data
        data = []

        # Store entry attributes for the athlete
        for entry in self._root.findall(
                './MEETS/MEET/CLUBS/CLUB[@code="{}"]/ATHLETES/ATHLETE'
                '[@athleteid="{}"]/ENTRIES/ENTRY'.format(club_id, athlete_id)):
            attributes = {}
            for key, value in entry.attrib.items():
                attributes[key] = value.strip()

            # Get MEETINFO data by additionally filtering by eventid
            event_id = attributes['eventid']
            for meetinfo in self._root.findall(
                    './MEETS/MEET/CLUBS/CLUB[@code="{}"]/ATHLETES/ATHLETE'
                    '[@athleteid="{}"]/ENTRIES/ENTRY[@eventid="{}"]/MEETINFO'
                    ''.format(club_id, athlete_id, event_id)):
                for key, value in meetinfo.attrib.items():
                    attributes[key] = value.strip()
            data.append(attributes)

        return data

    def _athlete_results(self, club_id, athlete_id):
        """Get all athlete information.

        Args:
            club_id: Club ID number
            athlete_id: Athlete ID

        Returns:
            data: List of dicts with information

        """
        # Get data
        data = []

        # Store results attributes for the athlete
        for result in self._root.findall(
                './MEETS/MEET/CLUBS/CLUB[@code="{}"]/ATHLETES/ATHLETE'
                '[@athleteid="{}"]/RESULTS/RESULT'
                ''.format(club_id, athlete_id)):
            attributes = {}
            for key, value in result.attrib.items():
                attributes[key] = value.strip()

            # Get the swimtime in seconds
            swimtime = attributes['swimtime']
            if ':' in swimtime:
                (hours, minutes, seconds) = swimtime.split(':')
                total_seconds = (int(hours) * 3600) + (
                    int(minutes) * 60) + float(seconds)
                attributes['time'] = '{}'.format(total_seconds)
            else:
                attributes['time'] = None

            # Get SPLITS data by additionally filtering by eventid
            attributes['splits'] = []
            event_id = attributes['eventid']
            for split in self._root.findall(
                    './MEETS/MEET/CLUBS/CLUB[@code="{}"]/ATHLETES/ATHLETE'
                    '[@athleteid="{}"]/RESULTS/RESULT[@eventid="{}"]'
                    '/SPLITS/SPLIT'
                    ''.format(club_id, athlete_id, event_id)):
                splits = []
                for key, value in split.attrib.items():
                    splits.append({key: value.strip()})
                attributes['splits'].append(splits)

            data.append(attributes)

        return data

    def athlete(self, athlete_id):
        """Get athlete information.

        Args:
            athlete_id: Athlete ID number

        Returns:
            data: dict with information. None if not found

        """
        # Get data
        data = None
        for athlete in self.athletes():
            if int(athlete_id) == int(athlete['vitals']['athleteid']):
                data = athlete

        return data

    def results(self, event_id):
        """Get results for an event.

        Args:
            event_id: Event ID number

        Returns:
            data: List of dicts with information

        """
        # Initialize key variables
        data = []

        # Get athlete data for event
        athletes = self.athletes()

        for athlete in athletes:
            if 'results' in athlete:
                for event in athlete['results']:
                    if 'eventid' in event:
                        if int(event['eventid']) == int(event_id):
                            result = {}
                            result['vitals'] = athlete['vitals']
                            result['results'] = [event]
                            data.append(result)

        return data

    def results_csv(self, _event_id):
        """Get results for an event.

        Args:
            _event_id: Event ID number

        Returns:
            data: List of dicts with information

        """
        # Initialize key variables
        event_id = str(_event_id)
        participants = self.results(event_id)
        event = self.event(event_id)
        meet = self.meet()
        data = []
        factor = 6

        # Get data for the meet
        city = meet[0]['city']
        nation = meet[0]['nation']
        course = meet[0]['course']
        meet = meet[0]['name']

        # Get data for participants
        for participant in participants:
            firstname = participant['vitals']['firstname']
            lastname = participant['vitals']['lastname']
            gender = participant['vitals']['gender']
            birthdate = participant['vitals']['birthdate']
            swimtime = participant['results'][0]['time']
            stroke = event['stroke']
            distance = event['distance']
            _round = event['round']

            # Don't process people with zero times
            if bool(swimtime) is False:
                continue

            # Get height and weight data
            values = self._height_weight(firstname, lastname, birthdate)
            if bool(values) is False:
                if self._with_na is True:
                    bmi = 'N/A'
                    speed = 'N/A'
                    speed_per_kg = 'N/A'
                    weight = 'N/A'
                    height = 'N/A'
                else:
                    continue
            else:
                (height, weight) = values

                _bmi = weight / ((height / 100) * (height / 100))
                bmi = str(round(_bmi, factor))

                _speed = float(distance) / float(swimtime)
                speed = str(round(_speed, factor))

                _speed_per_kg = _speed / weight
                speed_per_kg = str(round(_speed_per_kg, factor))

            # Get birthyear
            birthyear = int(birthdate.split('-')[0])

            # Create list for output ignoring None values it may contain
            output = [
                meet, city, nation, course,
                event_id, distance, stroke, _round,
                gender, firstname, lastname, birthyear,
                str(height), str(weight),
                bmi,
                speed_per_kg,
                speed,
                swimtime]
            if None in output:
                continue
            data.append(output)

        return data

    def allresults(self, stage=None):
        """Get results for all events.

        Args:
            stage: Round of event

        Returns:
            data: List of dicts with information

        """
        # Initialize key variables
        event_ids = []
        _data = []

        # Get results for each event
        for event in self.events(stage=stage):
            event_ids.append(int(event['eventid']))
        for event_id in sorted(event_ids):
            result = self.results(event_id)
            _data.extend(result)

        data = results_csv_sorter(_data)
        return data

    def allresults_csv(self, stage=None):
        """Get results for all events.

        Args:
            stage: Round of event

        Returns:
            data: List of lists with information

        """
        # Initialize key variables
        event_ids = []
        _data = []

        # Get results for each event
        for event in self.events(stage=stage):
            event_ids.append(int(event['eventid']))
        for event_id in sorted(event_ids):
            result = self.results_csv(event_id)
            _data.extend(result)

        data = results_csv_sorter(_data)
        return data

    def _height_weight(self, firstname, lastname, birthdate):
        """Get weight and height of athlete.

        Args:
            firstname: Athlete first name
            lastname: Athlete last name
            birthdate: Athlete birth date

        Returns:
            data: tuple of (height, weight)

        """
        # Initialize key variables
        data = None
        profiles = self._profiles

        # Get data
        if lastname in profiles:
            if firstname in profiles[lastname]:
                if birthdate in profiles[lastname][firstname]:
                    values = profiles[lastname][firstname][birthdate]
                    height = values['height']
                    weight = values['weight']
                    data = (height, weight)

        return data


def results_csv_sorter(_data):
    """Get results for all events.

    Args:
        _data: List of lists to sort

    Returns:
        data: Sorted list of lists

    """
    time_sorted = sorted(_data, key=operator.itemgetter(11), reverse=True)
    data = sorted(time_sorted, key=operator.itemgetter(
        0, 1, 2, 3, 4, 5, 6, 7, 8))
    return data
