"""Module to process FINA results files."""

# Standard imports
import xml.etree.ElementTree as ET
import operator
from pprint import pprint

# Fina imports
from fina import log


class File(object):
    """Process XML data from http://www.omegatiming.com."""

    def __init__(self, filename):
        """Method to instantiate the class.

        Args:
            filename: Name of file to process

        Returns:
            None

        """
        self._root = ET.parse(filename)

        # Verify the file version is correct
        for node in self._root.iter('LENEX'):
            if 'version' not in node.attrib:
                log_message = (
                    'This file {} is not supported.'.format(filename))
                log.log2die(1000, log_message)
            else:
                if node.attrib['version'] != '3.0':
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
                    item[key] = value

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
                        item[key] = value
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
                    vitals[key] = value
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
                attributes[key] = value

            # Get MEETINFO data by additionally filtering by eventid
            event_id = attributes['eventid']
            for meetinfo in self._root.findall(
                    './MEETS/MEET/CLUBS/CLUB[@code="{}"]/ATHLETES/ATHLETE'
                    '[@athleteid="{}"]/ENTRIES/ENTRY[@eventid="{}"]/MEETINFO'
                    ''.format(club_id, athlete_id, event_id)):
                for key, value in meetinfo.attrib.items():
                    attributes[key] = value
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
                attributes[key] = value

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
                    splits.append({key: value})
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

        # Get data for the meet
        city = meet[0]['city']
        nation = meet[0]['nation']
        course = meet[0]['course']
        name = meet[0]['name']

        # Get data for participants
        for participant in participants:
            firstname = participant['vitals']['firstname']
            lastname = participant['vitals']['lastname']
            gender = participant['vitals']['gender']
            swimtime = participant['results'][0]['time']
            stroke = event['stroke']
            distance = event['distance']
            _round = event['round']

            # Create list for output ignoring None values it may contain
            output = [
                name, city, nation, course,
                event_id, distance, stroke, _round,
                gender, firstname, lastname, swimtime]
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
