#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

# Python libraries and packages
import copy
import csv
import datetime
import os
import re
import time
import xlsxwriter
import multiprocessing as mp

# Entire scripts from src
from src.scripts.transit.stop.stop import Stop
from src.scripts.transit.route.route import Route
from src.scripts.transit.rider.errors import *

# Classes and variables from src
from src.scripts.constants import PATH
from src.scripts.transit.rider.constants import BEGIN, BASELINE, DATA_HEADER, INCREMENT, META_HEADER, INJECT_HEADER
from src.scripts.utils.IOutils import set_directory, txt_writer


__author__ = 'Michael Lockwood'
__github__ = 'mlockwood'
__projectclass__ = 'go'
__projectsubclass__ = 'transit'
__projectname__ = 'ridership.py'
__date__ = 'February2015'
__credits__ = None
__collaborators__ = None


class Sheet(object):

    metadata = {}
    meta_check = {}
    errors = []
    warnings = []
    injections = {}  # {stop: {joint_route: {(from, to): convert_stop}}}

    @staticmethod
    def process(directory='{}/data/ridership'.format(PATH)):
        Sheet.load_metadata(directory=directory)
        Sheet.load_data(directory=directory)

        for file in Sheet.meta_check:
            Sheet.errors += [MissingDatasheetError.get(file)]

        txt_writer(Sheet.errors, '{}/reports/ridership/errors.csv'.format(PATH))
        txt_writer(Sheet.warnings, '{}/reports/ridership/warnings.csv'.format(PATH))
        return True

    @staticmethod
    def load_metadata(directory='{}/data/ridership'.format(PATH)):
        reader = csv.reader(open('{}/metadata.csv'.format(directory), 'r', newline='', encoding="utf8"), delimiter=',',
                            quotechar='|')
        for row in reader:
            if row != META_HEADER:
                file = '{0}{1:02d}{2:02d}_{3}.csv'.format(row[0], int(row[1]), int(row[2]), row[3])
                Sheet.metadata[file] = row

        Sheet.meta_check = copy.deepcopy(Sheet.metadata)
        return True

    @staticmethod
    def load_injections(directory='{}/data/ridership'.format(PATH)):
        reader = csv.reader(open('{}/injections.csv'.format(directory), 'r', newline='', encoding="utf8"), delimiter=',',
                            quotechar='|')
        for row in reader:
            if row != INJECT_HEADER:
                date0 = datetime.datetime.strptime(row[2], '%Y%m%d') if row[2] else datetime.datetime.min
                date1 = datetime.datetime.strptime(row[3], '%Y%m%d') if row[3] else datetime.datetime.max
                if row[0] not in Sheet.injections:
                    Sheet.injections[row[0]] = {}
                if row[1] not in Sheet.injections[row[0]]:
                    Sheet.injections[row[0]][row[1]] = {}
                Sheet.injections[row[0]][row[1]][(date0, date1)] = row[4]
        return True

    @staticmethod
    def load_data(directory='{}/data/ridership'.format(PATH)):
        Sheet.load_injections(directory)

        files = []
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in [f for f in filenames if re.search('^\d{8}[_|\-]S\d+[A-Z]?\.csv$', f)]:
                # Check if metadata exists for the datasheet
                if filename in Sheet.metadata:
                    meta = Sheet.metadata[filename]
                    del Sheet.meta_check[filename]
                    files.append((dirpath, filename, meta, Sheet.injections))
                else:
                    Sheet.errors += [MissingMetadataError.get(filename)]

        p = mp.Pool()
        results = p.map(Sheet.load_file, files)

        for errors, warnings, records in results:
            # Add errors and warnings to Sheet
            Sheet.errors += errors
            Sheet.warnings += warnings

            # Add a Record object for each record
            for record in records:
                Record(*record)
        return True

    @staticmethod
    def load_file(args):
        records = []
        errors = []
        warnings = []

        file = '{}/{}'.format(args[0], args[1])
        meta = args[2]
        injections = args[3]
        reader = csv.reader(open(file, 'r', newline='', encoding="utf8"), delimiter=',', quotechar='|')

        # Validate metadata
        errors += Sheet.validate_meta(meta, file)

        # Handle each entry in the data
        r = 0
        entries = []
        overwrite = False
        for row in reader:
            r += 1
            if row != DATA_HEADER:
                # Validate entry
                on, off, time, count, errs, ow = Sheet.validate_entry(r, row, meta, injections, file)
                errors += errs
                if ow:
                    overwrite = True

                # Set record
                records.append([file] + meta[0:7] + [on, off, time, count])
                entries.append([on, time, count, off])

        # Overwrite file if necessary
        if overwrite:
            Sheet.overwrite(file, entries)

        # If no data, alert user just in case of error
        if r < 2:
            warnings += [EmptyDataWarning.get(file)]

        return errors, warnings, records

    @staticmethod
    def overwrite(file, entries):
        print('{} has been overwritten'.format(file))
        entries = [DATA_HEADER] + entries
        writer = open(file, 'w')
        for entry in entries:
            writer.write('{}\n'.format(','.join([str(s) for s in entry])))
        writer.close()

    @staticmethod
    def validate_meta(meta, file):
        errors = []
        i = 0
        while i < len(meta):
            if not re.sub(' ', '', meta[i]):
                errors += [MissingMetaValueError.get(file, META_HEADER[i])]
            i += 1
        return errors

    @staticmethod
    def validate_entry(r, entry, meta, injections, file):
        errors = []
        overwrite = False

        # Ignore blank rows and counts of 0
        if not re.sub(' ', '', ''.join(str(x) for x in entry)):
            return False
        elif entry[2] == '0':
            return False

        # Validate that every column has been completed for the record
        i = 0
        while i < len(entry):
            if not re.sub(' ', '', entry[i]):
                errors += [EntryError.get(file, r, DATA_HEADER[i])]
            i += 1

        # Stop validation and mapping
        # Boarding (on)
        on = Sheet.test_injection(entry[0], meta[4], datetime.datetime(int(meta[0]), int(meta[1]), int(meta[2])),
                                  injections)
        if on != entry[0]:
            overwrite = True

        if on not in Stop.locations:
            errors += [StopValidationError.get(file, 'Boarding', entry[0], r)]
            on = None

        # Deboarding (off)
        off = Sheet.test_injection(entry[3], meta[4], datetime.datetime(int(meta[0]), int(meta[1]), int(meta[2])),
                                   injections)

        if off != entry[3]:
            overwrite = True

        if off not in Stop.locations:
            errors += [StopValidationError.get(file, 'Deboarding', entry[3], r)]
            off = None

        # Time validation
        time = re.sub(':', '', entry[1])
        if len(time) > 4:
            errors += [TimeValidationError.get(file, time, r)]
            time = 'xxxx'
        else:
            try:
                time = str(int(time[:-2])) + ':' + str(time[-2:])
            except TypeError:
                errors += [TimeValidationError.get(file, time, r)]
                time = 'xxxx'
            except ValueError:
                if len(time) == 2:
                    time = '00:{}'.format(time)
                elif len(time) == 1:
                    time = '00:0{}'.format(time)
                else:
                    errors += [TimeValidationError.get(file, time, r)]
                    time = 'xxxx'

        # Count validation
        try:
            count = int(entry[2])
        except TypeError:
            errors += [CountValidationError.get(file, entry[2], r)]
            count = 0

        return on, off, time, count, errors, overwrite

    @staticmethod
    def test_injection(stop, route, date, injections):
        if stop in injections:
            if route in injections[stop]:
                for date_range in injections[stop][route]:
                    if date_range[0] < date < date_range[1]:
                        return injections[stop][route][date_range]
        return stop


class Record(object):

    objects = {}
    ID_generator = 1
    matrix_header = ['ID', 'Year', 'Month', 'Day', 'Weekday', 'Sheet', 'Route', 'On_Route', 'Off_Route', 'Driver',
                     'License', 'Time', 'On_Stop', 'Off_Stop', 'Count']
    matrix = [matrix_header]

    def __init__(self, file, year, month, day, sheet, route, driver, veh_license, on_stop, off_stop, time,
                 count):
        # Default values
        self.file = file
        self.year = int(year)
        self.month = int(month)
        self.day = int(day)
        self.date = datetime.datetime(self.year, self.month, self.day)
        self.dow = str(self.date.isocalendar()[2])
        self.sheet = sheet
        self.route = route
        self.driver = driver
        self.license = veh_license
        self.on_stop = on_stop
        self.off_stop = off_stop
        self.time = time
        self.count = count

        # Set pseudo route values
        self.on_pseudo = self.get_pseudo(on_stop)
        self.off_pseudo = self.get_pseudo(off_stop)

        if not self.on_pseudo and self.off_pseudo:
            self.on_pseudo = self.off_pseudo

        elif self.on_pseudo and not self.off_pseudo:
            self.off_pseudo = self.on_pseudo

        if not self.on_pseudo and not self.off_pseudo:
            self.on_pseudo = re.split('&', self.route)[0]
            self.off_pseudo = re.split('&', self.route)[-1]

        # Final attributions
        self.ID = hex(Record.ID_generator)
        Record.ID_generator += 1
        Record.objects[self.ID] = self
        self.append_record()
        # Add record to the date it pertains
        Period.add_count(self.date, self.count)

    def get_pseudo(self, stop):
        if str(stop) in ['100', '300']:
            return None

        elif re.sub('[A-Za-z]', '', self.sheet) in ['8', '9']:
            return 'Evening'

        elif self.sheet.lower() == 's5z':
            return 'Morning'

        elif self.date >= datetime.datetime(2016, 4, 25) and self.sheet.lower() == 's5a':
            return 'Morning'

        else:
            routes = re.split('&', self.route)
            for route_id in routes:
                if Route.query_route(int(route_id), self.date, stop):
                    return route_id

            if stop != 'None' and stop:
                Sheet.errors += [StopUnavailableForRouteError.get(self.file, stop, self.route)]
        return 'Unmatched'

    def append_record(self):
        Record.matrix.append([self.ID, self.year, self.month, self.day, self.dow, self.sheet, self.route,
                              self.on_pseudo, self.off_pseudo, self.driver, self.license, self.time, self.on_stop,
                              self.off_stop, self.count])
        return True

    @staticmethod
    def publish_matrix():
        txt_writer(Record.matrix, '{}/reports/ridership/records.csv'.format(PATH))
        return True
    

class Period(object):

    objects = {}
    periods = {('total', 'total'): {}}

    def __init__(self, date):
        self.date = date
        self.count = 0
        self.average = 0
        self.straight_line = INCREMENT * abs(date - BEGIN).days + BASELINE
        self.set_week()
        self.set_month()
        self.set_year()
        self.set_total()
        Period.objects[date] = self

    @staticmethod
    def add_count(date, count):
        if date not in Period.objects:
            Period(date)
        Period.objects[date].count += count
        return True

    @staticmethod
    def set_averages():
        for date in sorted(Period.objects.keys()):
            day = Period.objects[date]
            prev = Period.seek_prev_dow(date)
            prev = prev.average if prev else (0, 0, 0)
            day.average = ((prev[1] + day.count) / (prev[2] + 1), prev[1] + day.count, prev[2] + 1)
        return True

    @staticmethod
    def seek_prev_dow(date):
        if date - datetime.timedelta(days=7) in Period.objects:
            return Period.objects[date - datetime.timedelta(days=7)]
        elif date < datetime.datetime(2015, 8, 31):
            return None
        else:
            return Period.seek_prev_dow(date - datetime.timedelta(days=7))

    @staticmethod
    def publish():
        outputs = []
        for key in Period.periods:
            if not os.path.exists('{}/reports/ridership/{}'.format(PATH, key[1])):
                os.makedirs('{}/reports/ridership/{}'.format(PATH, key[1]))
            filename = '{}/reports/ridership/{}/{}.xlsx'.format(PATH, key[1], key[0])
            outputs.append((Period.periods[key], filename))

        p = mp.Pool()
        p.map(Period.write_file, outputs)
        return True

    @staticmethod
    def write_file(args):
        obj = args[0]

        # Open workbook and worksheet
        workbook = xlsxwriter.Workbook(args[1])
        worksheet = workbook.add_worksheet('Ridership')
        chart = workbook.add_chart({'type': 'line'})

        # Set column widths
        worksheet.set_column('A:A', 12)
        worksheet.set_column('B:B', 12)
        worksheet.set_column('C:C', 12)
        worksheet.set_column('D:D', 12)
        worksheet.set_column('E:E', 12)

        # Write header
        worksheet.write_row('A1', ['Weekday', 'Date', 'Riders', 'Average', 'Pilot Target'])

        # Write data
        row = 2
        for day in sorted(obj.keys()):
            worksheet.write_row('A' + str(row),
                [obj[day].date.strftime('%A'),
                 obj[day].date.strftime('%d %b %Y'),
                 obj[day].count,
                 round(obj[day].average[0], 2),
                 round(obj[day].straight_line, 2)])
            row += 1

        # Set chart series
        chart.add_series({'name': 'Ridership',
                          'categories': ('=Ridership!$B$2:$B$' +
                                         str(row - 1)),
                          'values': '=Ridership!$C$2:$C$' + str(row - 1),
                          'line': {'color': '#008000'},
                          })
        chart.add_series({'name': 'Average',
                          'categories': ('=Ridership!$B$2:$B$' +
                                         str(row - 1)),
                          'values': '=Ridership!$D$2:$D$' + str(row - 1),
                          'line': {'color': '#000080'},
                          })
        chart.add_series({'name': 'Pilot',
                          'categories': ('=Ridership!$B$2:$B$' +
                                         str(row - 1)),
                          'values': '=Ridership!$E$2:$E$' + str(row - 1),
                          'line': {'color': '#808080'},
                          })

        # Set chart ancillary information
        chart.set_title({'name': 'GO Transit Ridership'})
        chart.set_x_axis({'name': 'Day'})
        chart.set_y_axis({'name': 'Riders'})

        # Insert chart into the worksheet
        worksheet.insert_chart('A' + str(row + 2), chart, {'x_offset': 10, 'y_offset': 10})
        workbook.close()
        return True

    def set_week(self):
        week_key = '{0}_{1:2d}'.format(self.date.isocalendar()[0], self.date.isocalendar()[1])
        if (week_key, 'weekly') not in Period.periods:
            Period.periods[(week_key, 'weekly')] = {}
        Period.periods[(week_key, 'weekly')][self.date] = self
        return True

    def set_month(self):
        month_key = '{}_{}'.format(str(self.date.year), str(self.date.month))
        if (month_key, 'monthly') not in Period.periods:
            Period.periods[(month_key, 'monthly')] = {}
        Period.periods[(month_key, 'monthly')][self.date] = self
        return True

    def set_year(self):
        if (self.date.year, 'annual') not in Period.periods:
            Period.periods[(self.date.year, 'annual')] = {}
        Period.periods[(self.date.year, 'annual')][self.date] = self
        return True

    def set_total(self):
        Period.periods[('total', 'total')][self.date] = self
        return True


if __name__ == "__main__":
    set_directory('{}/reports/ridership'.format(PATH))
    start = time.clock()
    Sheet.process()
    print('Sheet processing complete', time.clock() - start)
    Record.publish_matrix()
    print('Matrix published', time.clock() - start)
    Period.set_averages()
    print('Averages set', time.clock() - start)
    Period.publish()
    print('Publishing complete', time.clock() - start)

