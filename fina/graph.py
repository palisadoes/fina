"""Module to process FINA results files."""

# Standard imports
import csv
import hashlib
from collections import defaultdict
import numpy as np
from pprint import pprint

# pip3 imports
import matplotlib.pyplot as plt


class Data(object):
    """Process Database data."""

    def __init__(self, filename, fastest=True, course=None):
        """Method to instantiate the class.

        Args:
            filename: Name of file to process
            fastest: Only plot the fastest times for each athlete if True

        Returns:
            None

        """
        # Initialize key variables
        self._filename = filename
        self._fastest = fastest

        # Generate globally necessary data
        self._events = self._read_database(course=course)
        self._superkeys = sorted(self._events.keys())

    def bmi(self, stroke, distance, gender):
        """Return list of bmi values sorted by superkey.

        Args:
            stroke: Stroke Name
            distance: Distance of Event
            gender: gender of Participants

        Returns:
            data: list of BMIs

        """
        # Initialize key variables
        measurement = 'bmi'
        data = self._measurements(stroke, distance, gender, measurement)
        return data

    def speed(self, stroke, distance, gender):
        """Return list of speed values sorted by superkey.

        Args:
            stroke: Stroke Name
            distance: Distance of Event
            gender: gender of Participants

        Returns:
            data: list of BMIs

        """
        # Initialize key variables
        measurement = 'speed'
        data = self._measurements(stroke, distance, gender, measurement)
        return data

    def kgspeed(self, stroke, distance, gender):
        """Return list of speed values sorted by superkey.

        Args:
            stroke: Stroke Name
            distance: Distance of Event
            gender: gender of Participants

        Returns:
            data: list of BMIs

        """
        # Initialize key variables
        measurement = 'speed_per_kg'
        data = self._measurements(stroke, distance, gender, measurement)
        return data

    def _measurements(self, _stroke, _distance, gender, measurement):
        """Return list of bmi values sorted by superkey.

        Args:
            _stroke: Stroke Name
            _distance: Distance of Event
            gender: gender of Participants
            measurement: Measure to get

        Returns:
            data: list of BMIs

        """
        # Initialize key variables
        stroke = _stroke.upper()
        distance = str(int(_distance))
        data = []

        for superkey in self._superkeys:
            if gender is None:
                if stroke in self._events[superkey]:
                    if distance in self._events[superkey][stroke]:
                        # Get value for any gender
                        for gender_key in sorted(
                                self._events[
                                    superkey][stroke][distance].keys()):
                            value = self._events[superkey][
                                stroke][distance][gender_key][measurement]
                            data.append(value)
            else:
                if stroke in self._events[superkey]:
                    if distance in self._events[superkey][stroke]:
                        if gender in self._events[superkey][stroke][distance]:
                            value = self._events[superkey][
                                stroke][distance][gender][measurement]
                            data.append(value)

        return data

    def _read_database(self, course=None):
        """Process the database file.

        Args:
            course: Course to filter by

        Returns:
            events: Anonymized dict of best results per athlete keyed by
                hash, stroke, distance and gender

        """
        # Initialize key variables
        filename = self._filename
        athletes = {}
        delimiter = '|'
        events = defaultdict(lambda: defaultdict(
            lambda: defaultdict(lambda: defaultdict())))

        # Read CSV file
        with open(filename) as csvfile:
            f_handle = csv.reader(csvfile, delimiter=delimiter)
            for row in f_handle:
                # Filter by course type
                if course is not None:
                    course_type = row[3].upper()
                    if course_type != course.upper():
                        continue

                # Contiue processing the row
                (_, _, _, _, _, _time, _, superkey) = _process_row(
                    row, fastest=self._fastest)

                # Get the fastest time for each athlete (minimum duration)
                if superkey in athletes:
                    athletes[superkey] = min(_time, athletes[superkey])
                else:
                    athletes[superkey] = _time

        # Read CSV file again
        with open(filename) as csvfile:
            f_handle = csv.reader(csvfile, delimiter=delimiter)
            for row in f_handle:
                # Filter by course type (Again)
                if course is not None:
                    course_type = row[3].upper()
                    if course_type != course.upper():
                        continue

                (_, _, gender, stroke,
                 distance, _time, data, superkey) = _process_row(
                    row, fastest=self._fastest)
                if athletes[superkey] == _time:
                    events[superkey][stroke][distance][gender] = data

        return events


class Graph(object):
    """Create graphs."""

    def __init__(self, filename, fastest=True, course=None):
        """Method to instantiate the class.

        Args:
            filename: Name of file to process

        Returns:
            None

        """
        # Initialize key variables
        self.course = course

        # Create lookup tables
        self._database = Data(filename, fastest=fastest, course=self.course)
        self._strokes = {
            'FLY': 'FLY',
            'BUT': 'FLY',
            'FRE': 'FREE',
            'BRE': 'BREAST',
            'BAC': 'BACK',
            'MED': 'MEDLEY'
        }
        self._title_strokes = {
            'FLY': 'Butterfly',
            'BUT': 'Butterfly',
            'FRE': 'Freestyle',
            'BRE': 'Breaststroke',
            'BAC': 'Backstroke',
            'MED': 'Individual Medley'
        }
        self._title_gender = {
            'M': "Men's",
            'F': "Women's",
            None: "Combined Men's and Women's",
            'B': "Men's and Women's"
        }
        self._colors_gender = {
            'M': '#4F81BD',
            'F': '#000000',
            None: '#FFA500',
        }
        self._colors_line = {
            'efficiency': '#0000FF',
            'speed': '#00FFFF'
        }

    def _shared(self, _stroke, distance, gender=None):
        """Plot BMI vs Speed for a given event and gender.

        Args:
            _stroke: Event stroke
            distance: Event distance
            gender: Gender

        Returns:
            None

        """
        # Initialize key variables
        stroke_abbreviation = _stroke[0:3].upper()
        stroke = self._strokes[stroke_abbreviation]

        # Get the proper gender
        if gender is None:
            _gender = None
        elif gender.upper()[0] == 'M':
            _gender = 'M'
        elif gender.upper()[0] == 'F':
            _gender = 'F'
        elif gender.upper()[0] == 'W':
            _gender = 'F'
        else:
            _gender = 'B'

        # Create plot title
        title = (
            '{} {}m {} ({})'.format(
                self._title_gender[_gender],
                distance,
                self._title_strokes[stroke_abbreviation],
                self.course.upper()))

        result = (stroke, _gender, title)
        return result

    def bmi_speed(self, _stroke, distance, gender=None):
        """Plot BMI vs Speed for a given event and gender.

        Args:
            _stroke: Event stroke
            distance: Event distance

        Returns:
            None

        """
        # Do multiple charts if necessary
        (stroke, _gender, _) = self._shared(_stroke, distance, gender)
        if _gender == 'B':
            self._bmi_speed_2(stroke, distance)
        else:
            self._bmi_speed_1(stroke, distance, gender=gender)

    def _bmi_speed_1(self, _stroke, distance, gender=None):
        """Plot BMI vs Speed for a given event and gender.

        Args:
            _stroke: Event stroke
            distance: Event distance

        Returns:
            None

        """
        # Initialize key variables
        (stroke, _gender, title) = self._shared(_stroke, distance, gender)

        # Get values to plot
        x_values = self._database.speed(stroke, distance, _gender)
        y_values = self._database.bmi(stroke, distance, _gender)

        print(len(x_values))

        '''
        Create plot object in memory.

         facecolors:
           The string ‘none’ to plot unfilled outlines
         edgecolors:
            The string ‘none’ to plot faces with no outlines
        '''
        plt.scatter(
            x_values, y_values,
            marker='o',
            facecolors=self._colors_gender[_gender],
            alpha=0.5,
            label=self._title_gender[_gender].replace('\'s', ''))

        # Get the X axis min max to be used in chart for scaling
        x_autoscale_min, _ = plt.xlim()

        # Horizontal line at maximum speed y value
        speed_max = max(x_values)
        bmi_of_max_speed = y_values[x_values.index(speed_max)]
        plt.axhline(
            y=bmi_of_max_speed,
            label=('BMI of Max Speed: {0:.3f}'.format(bmi_of_max_speed)),
            linestyle='dashed',
            linewidth=1, color=self._colors_line['speed'])

        # Create plot title
        plt.suptitle(title)
        plt.title('BMI vs. Speed', fontsize='smaller')

        # Create plot legend based on plot label
        plt.legend()

        # Create Axes labels
        plt.xlabel('Speed (m/s)')
        plt.ylabel('BMI')

        # Display plot
        plt.show()

    def _bmi_speed_2(self, _stroke, distance):
        """Plot BMI vs Speed for a given event and gender.

        Args:
            _stroke: Event stroke
            distance: Event distance

        Returns:
            None

        """
        # Initialize key variables
        genders = ['M', 'F']
        data = {}
        (stroke, _gender, title) = self._shared(_stroke, distance, 'B')

        # Get values to plot
        for gender in genders:
            # Get values to plot
            data[gender] = {
                'x': self._database.speed(stroke, distance, gender),
                'y': self._database.bmi(stroke, distance, gender)
            }

        '''
        Create plot object in memory.

         facecolors:
           The string ‘none’ to plot unfilled outlines
         edgecolors:
            The string ‘none’ to plot faces with no outlines
        '''
        for gender in genders:
            x_values = data[gender]['x']
            y_values = data[gender]['y']
            plt.scatter(
                x_values, y_values,
                marker='o',
                facecolors=self._colors_gender[gender],
                alpha=0.5,
                label=self._title_gender[gender].replace('\'s', ''))

        # Create plot title
        plt.suptitle(title)
        plt.title('BMI vs. Speed', fontsize='smaller')

        # Create plot legend based on plot label
        plt.legend()

        # Create Axes labels
        plt.xlabel('Speed (m/s)')
        plt.ylabel('BMI')

        # Display plot
        plt.show()

    def bmi_kgspeed(self, _stroke, distance, gender=None):
        """Plot BMI vs Speed for a given event and gender.

        Args:
            _stroke: Event stroke
            distance: Event distance

        Returns:
            None

        """
        # Do multiple charts if necessary
        (stroke, _gender, _) = self._shared(_stroke, distance, gender)
        if _gender == 'B':
            self._bmi_kgspeed_2(stroke, distance)
        else:
            self._bmi_kgspeed_1(stroke, distance, gender=gender)

    def _bmi_kgspeed_1(self, _stroke, distance, gender=None):
        """Plot BMI vs Speed for a given event and gender.

        Args:
            _stroke: Event stroke
            distance: Event distance

        Returns:
            None

        """
        # Initialize key variables
        (stroke, _gender, title) = self._shared(_stroke, distance, gender)

        # Get values to plot
        x_values = self._database.kgspeed(stroke, distance, _gender)
        y_values = self._database.bmi(stroke, distance, _gender)
        speeds = self._database.speed(stroke, distance, _gender)

        print(len(x_values))

        '''
        Create plot object in memory.

         facecolors:
           The string ‘none’ to plot unfilled outlines
         edgecolors:
            The string ‘none’ to plot faces with no outlines
        '''
        plt.scatter(
            x_values, y_values,
            marker='o',
            facecolors=self._colors_gender[_gender],
            alpha=0.5,
            label=self._title_gender[_gender].replace('\'s', ''))

        # Create plot title
        plt.suptitle(title)
        plt.title('BMI vs. Swimming Efficiency', fontsize='smaller')

        # Create linear trendline (linear fitting)
        function = np.poly1d(np.polyfit(x_values, y_values, 1))
        plt.plot(
            x_values, function(x_values),
            color=self._colors_gender[_gender],
            linestyle='solid',
            linewidth=1,
            antialiased=False)

        # Horizontal line at minimum y value
        x_max = max(x_values)
        bmi_of_max_efficiency = y_values[x_values.index(x_max)]
        plt.axhline(
            y=bmi_of_max_efficiency,
            label=(
                'BMI of Max Efficiency: {0:.3f}'
                ''.format(bmi_of_max_efficiency)),
            linestyle='dashed',
            linewidth=1,
            color=self._colors_line['efficiency'])

        # Horizontal line at maximum speed y value
        speed_max = max(speeds)
        bmi_of_max_speed = y_values[speeds.index(speed_max)]
        plt.axhline(
            y=bmi_of_max_speed,
            label=('BMI of Max Speed: {0:.3f}'.format(bmi_of_max_speed)),
            linestyle='dashed',
            linewidth=1,
            color=self._colors_line['speed'])

        # Create plot legend based on plot label
        plt.legend()

        # Create Axes labels
        plt.xlabel('Speed / Kg (m/Kgs)')
        plt.ylabel('BMI')

        # Display plot
        plt.show()

    def _bmi_kgspeed_2(self, _stroke, distance):
        """Plot BMI vs Speed for a given event and both genders.

        Args:
            _stroke: Event stroke
            distance: Event distance

        Returns:
            None

        """
        # Initialize key variables
        genders = ['M', 'F']
        data = {}
        (stroke, _gender, title) = self._shared(_stroke, distance, 'B')

        # Get values to plot
        for gender in genders:
            data[gender] = {
                'x': self._database.kgspeed(stroke, distance, gender),
                'y': self._database.bmi(stroke, distance, gender),
                'speed': self._database.speed(stroke, distance, gender)
            }

        # print(len(x_values))

        '''
        Create plot object in memory.

         facecolors:
           The string ‘none’ to plot unfilled outlines
         edgecolors:
            The string ‘none’ to plot faces with no outlines
        '''
        for gender in genders:
            x_values = data[gender]['x']
            y_values = data[gender]['y']
            plt.scatter(
                x_values, y_values,
                marker='o',
                facecolors=self._colors_gender[gender],
                alpha=0.5,
                label=self._title_gender[gender].replace('\'s', ''))

        # Create plot title
        plt.suptitle(title)
        plt.title('BMI vs. Swimming Efficiency', fontsize='smaller')

        # Create plot legend based on plot label
        plt.legend()

        # Create Axes labels
        plt.xlabel('Speed / Kg (m/Kgs)')
        plt.ylabel('BMI')

        # Display plot
        plt.show()

    def speed_kgspeed(self, _stroke, distance, gender=None):
        """Plot Speed / Kg vs Speed for a given event and gender.

        Args:
            _stroke: Event stroke
            distance: Event distance

        Returns:
            None

        """
        # Do multiple charts if necessary
        (stroke, _gender, _) = self._shared(_stroke, distance, gender)
        if _gender == 'B':
            self._speed_kgspeed_2(stroke, distance)
        else:
            self._speed_kgspeed_1(stroke, distance, gender=gender)

    def _speed_kgspeed_1(self, _stroke, distance, gender=None):
        """Plot Speed / Kg vs Speed for a given event and gender.

        Args:
            _stroke: Event stroke
            distance: Event distance

        Returns:
            None

        """
        # Initialize key variables
        (stroke, _gender, title) = self._shared(_stroke, distance, gender)

        # Get values to plot
        x_values = self._database.speed(stroke, distance, _gender)
        y_values = self._database.kgspeed(stroke, distance, _gender)
        bmis = self._database.bmi(stroke, distance, _gender)

        print(len(x_values))

        '''
        Create plot object in memory.

         facecolors:
           The string ‘none’ to plot unfilled outlines
         edgecolors:
            The string ‘none’ to plot faces with no outlines
        '''
        plt.scatter(
            x_values, y_values,
            marker='o',
            facecolors=self._colors_gender[_gender],
            alpha=0.5,
            label=self._title_gender[_gender].replace('\'s', ''))

        # Horizontal line at maximum efficiency y value
        y_max = max(y_values)
        x_max = max(x_values)
        bmi_of_max_efficiency = bmis[y_values.index(y_max)]
        plt.axhline(
            y=y_max,
            label=(
                'Max Efficiency (BMI: {0:.3f})'
                ''.format(bmi_of_max_efficiency)),
            linestyle='dashed',
            linewidth=1,
            color=self._colors_line['efficiency'])

        # Horizontal line at maximum speed y value
        bmi_of_max_speed = bmis[x_values.index(x_max)]
        plt.axhline(
            y=y_values[x_values.index(x_max)],
            label=(
                'Efficiency at Max Speed (BMI: {0:.3f})'
                ''.format(bmi_of_max_speed)),
            linestyle='dashed',
            linewidth=1,
            color=self._colors_line['speed'])

        # Create plot title
        plt.suptitle(title)
        plt.title('Swimming Efficiency vs. Speed', fontsize='smaller')

        # Create plot legend based on plot label
        plt.legend()

        # Create Axes labels
        plt.xlabel('Speed')
        plt.ylabel('Speed / Kg (m/Kgs)')

        # Display plot
        plt.show()

    def _speed_kgspeed_2(self, _stroke, distance):
        """Plot Speed / Kg vs Speed for a given event and gender.

        Args:
            _stroke: Event stroke
            distance: Event distance

        Returns:
            None

        """
        # Initialize key variables
        genders = ['M', 'F']
        data = {}
        (stroke, _gender, title) = self._shared(_stroke, distance, 'B')

        # Get values to plot
        for gender in genders:
            data[gender] = {
                'x': self._database.speed(stroke, distance, gender),
                'y': self._database.kgspeed(stroke, distance, gender),
                'bmis': self._database.bmi(stroke, distance, gender)
            }

        # print(len(x_values))

        '''
        Create plot object in memory.

         facecolors:
           The string ‘none’ to plot unfilled outlines
         edgecolors:
            The string ‘none’ to plot faces with no outlines
        '''
        for gender in genders:
            x_values = data[gender]['x']
            y_values = data[gender]['y']
            plt.scatter(
                x_values, y_values,
                marker='o',
                facecolors=self._colors_gender[gender],
                alpha=0.5,
                label=self._title_gender[gender].replace('\'s', ''))
            print(gender)

        # Create plot title
        plt.suptitle(title)
        plt.title('Swimming Efficiency vs. Speed', fontsize='smaller')

        # Create plot legend based on plot label
        plt.legend()

        # Create Axes labels
        plt.xlabel('Speed')
        plt.ylabel('Speed / Kg (m/Kgs)')

        # Display plot
        plt.show()


def _process_row(row, fastest=True):
    """Process the database row.

    Args:
        row: Database row

    Returns:
        data: tuple of important row data

    """
    firstname = row[9]
    lastname = row[10]
    # birthyear = int(float(row[11]))
    gender = row[8]
    stroke = row[6]
    distance = str(int(float(row[5])))
    _time = float(row[-1])
    _data = {
        'bmi': float(row[14]),
        'speed_per_kg': float(row[15]),
        'speed': float(row[16])}

    if fastest is True:
        event = ''
    else:
        event = '{}{}{}{}{}'.format(
            row[0], row[1], row[2], row[3], int(float(row[4])))

    superkey = hashlib.sha256(
        bytes('{}{}{}{}{}'.format(
            firstname, lastname, stroke, distance, event),
        'utf-8')).hexdigest()
    data = (
        firstname, lastname, gender, stroke,
        distance, _time, _data, superkey)

    return data
