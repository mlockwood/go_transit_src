#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

# Python libraries and packages
import csv
import datetime
import os
import re
import xlsxwriter
import multiprocessing as mp

# Entire scripts from src
import src.scripts.transit.stop.stop as st
import src.scripts.transit.ridership.errors as RidershipErrors

# Classes and variables from src
from src.scripts.transit.constants import PATH, BEGIN, BASELINE, INCREMENT
from src.scripts.transit.ridership.constants import CHARS, HEADER, STANDARD, META_MAP


__author__ = 'Michael Lockwood'
__github__ = 'mlockwood'
__projectclass__ = 'go'
__projectsubclass__ = 'transit'
__projectname__ = 'ridership.py'
__date__ = 'February2015'
__credits__ = None
__collaborators__ = None


class Sheet(object):

    objects = {}
    structure = {}
    sheet_names = {}
    rewrite = {}
    header_0 = 'Boarding'

    def __init__(self, file):
        self.file = file
        self.start_shift = ''
        self.time_key = 0
        self.records = {}
        self.entries = []
        self.temp = {}
        self.year = None
        self.month = None
        self.day = None
        self.strp = None
        self.schedule = None
        Sheet.objects[self.file] = self

    @staticmethod
    def process():
        # obj_list = []
        for dirpath, dirnames, filenames in os.walk(PATH + '/data'):
            if 'archive' in dirpath or 'archive' in dirnames:
                continue
            for filename in [f for f in filenames if re.search('\d{6}_S\d', f)]:
                obj = Sheet((str(dirpath) + '/' + str(filename)))
                obj.read_sheet()
        """
        # This section is not working, it is attempting to multithread the
        # reading of the datasheets but has pickling problems due to the use
        # of objects.
        pool = mp.Pool()
        results = pool.map_async(Sheet.read_sheet, obj_list)
        """
        #  Sheet.write_sheets()
        return True

    def read_sheet(self):
        reader = csv.reader(open(self.file, 'r', newline=''),
                            delimiter=',', quotechar='|')
        meta = False
        columns = False
        data = False
        direction = '1'
        meta_D = {}
        for row in reader:
            # <Handle Types>
            # Blank row handle
            if not re.sub(' ', '', ''.join(row)):
                continue
            
            # Metadata boolean handle
            elif row[0] == 'METADATA':
                meta = True
                continue
            
            # Data boolean handle
            elif row[0] == 'DATA':
                data = True
                columns = False
                meta = False
                continue
            # </Handle Types>
            
            # Metadata
            if meta:
                # Handle metadata category
                cur_meta = re.sub(' ', '', str(row[0]).lower())
                if cur_meta not in STANDARD:
                    # FIX STANDARD, MAPPING, and OVERRIDING-------------------------------------------------------------
                    if cur_meta in META_MAP:
                        if META_MAP[cur_meta] != '<delete>':
                            cur_meta = META_MAP[cur_meta]
                
                # Handle metadata value
                cur_value = str(row[1])
                #if cur_meta in Sheet.override:
                #    cur_value = Sheet.override[cur_meta]
                
                # Add meta category, value to meta_D and Sheet object
                #if cur_meta not in Sheet.delete:
                meta_D[cur_meta] = cur_value
                try:
                    exec('self.' + cur_meta + '=\'' + cur_value + '\'')
                except:
                    raise ValueError('Metadata error in ' + cur_value)
                        
            # Data
            if data:
                if row != Sheet.header_0:
                    self.entries.append(row)
        
        # Add sheet to the general sheet structure
        self.set_structure()

        # Validation
        self.validate(data, meta_D)

        # Actually process record using the latest version methodology
        self.set_records()
        return True

    def set_structure(self):

        if not (self.year, self.month, self.day) in Sheet.structure:
            Sheet.structure[(self.year, self.month, self.day)] = {}
        if self.schedule not in Sheet.structure[(self.year, self.month, self.day)]:
            Sheet.structure[(self.year, self.month, self.day)][self.schedule] = {}

        if self.start_shift:
            Sheet.structure[(self.year, self.month, self.day)][self.schedule][
                int(re.sub(':', '', self.start_shift))] = True
            self.time_key = int(re.sub(':', '', self.start_shift))
        else:
            Sheet.structure[(self.year, self.month, self.day)][self.schedule][self.time_key] = True
        return True

    def validate(self, data, meta_D):
        # If no data, alert user just in case of error
        if not data:
            print(self.file, 'does not contain any data.')

        # Merge former separated route format
        delete = []
        route_meta = []
        for meta in meta_D:
            if meta.lower() == 'route':
                continue
            if re.search('route[\d]*', meta.lower()):
                if re.search('y', meta_D[meta].lower()):
                    route_meta.append(re.sub('route', '', meta.lower()))
                delete.append(meta)
        # Delete old meta keys from meta_D
        for meta in delete:
            del meta_D[meta]
        # Add new meta key for route
        if route_meta:
            meta_D['route'] = '&'.join(sorted(route_meta))
            exec('self.route=\'&\'.join(sorted(route_meta))')

        # Check standard metadata variables
        for meta in STANDARD:
            if meta not in meta_D:
                if STANDARD[meta] == '<required>':
                    raise RidershipErrors.MissingMetadataError('{} is missing metadata for "{}".'.format(self.file,
                                                                                                         meta))
                meta_D[meta] = STANDARD[meta]
                exec('self.' + meta + '=' + STANDARD[meta])

        # Check if the naming convention matches the standard
        match = re.search('\d{6}', self.file)
        if not match:
            RidershipErrors.NamingConventionWarning('Naming convention error with file {}'.format(self.file))

        # Build date strp such as '20160831' from metadata
        self.strp = '{}{:02d}{:02d}'.format(int(self.year), int(self.month), int(self.day))
        self.date = datetime.datetime.strptime(self.strp, '%Y%m%d')

        # Construct date strp from file name
        f_year = '20' + self.file[match.span()[0]:match.span()[0] + 2]
        f_month = self.file[match.span()[0] + 2:match.span()[0] + 4]
        f_day = self.file[match.span()[0] + 4:match.span()[0] + 6]

        # Check if the file name matches the year, month, and day file contents
        if self.strp != '{}{}{}'.format(f_year, f_month, f_day):
            RidershipErrors.FileNameMismatchWarning('year, month, day do not match contents for file' +
                                                    ' {}.'.format(self.file))
        return True

    def set_records(self):
        R = 1
        for entry in self.entries:
            # Ignore headers, blank rows and counts of 0
            if entry[0] == Sheet.header_0:
                continue
            elif not re.sub(' ', '', ''.join(str(x) for x in entry)):
                continue
            elif entry[2] == '0':
                continue

            # Validate that every column has been completed for the record
            i = 0
            while i < len(entry):
                if not re.sub(' ', '', entry[i]):
                    raise RidershipErrors.EntryError('{} record in row {} does not have a '.format(self.file, R) +
                                                     '{}'.format(HEADER[i]))
                i += 1
            
            # Stop validation and mapping
            # Boarding (on)
            try:
                on = st.Historic.historic_conversion(self.strp, entry[0]).stop_id
            except:
                raise RidershipErrors.StopValidationError('{} record in row {} with boarding '.format(self.file, R) +
                                                          '{} could not be found in the Stop lookup.'.format(entry[0]))

            # Deboarding (off)
            try:
                off = st.Historic.historic_conversion(self.strp, entry[3]).stop_id
            except:
                raise RidershipErrors.StopValidationError('{} record in row {} with deboarding '.format(self.file, R) +
                                                          '{} could not be found in the Stop lookup.'.format(entry[3]))

            # Set record
            record = Record(self.year, self.month, self.day, self.sheet, self.route, self.driver, self.schedule,
                            self.license, entry[1], on, off, entry[2])
            self.records[(on, entry[1], off)] = record
            R += 1
        return True


class Record(object):

    objects = {}
    ID_generator = 1
    matrix_header = ['ID', 'Year', 'Month', 'Day', 'Weekday', 'Sheet', 'Route', 'Driver', 'Schedule', 'License', 'Time',
                     'On_Stop', 'Off_Stop', 'Count']
    matrix = [matrix_header]

    def __init__(self, year, month, day, sheet, route, driver, schedule, veh_license, time, on_stop, off_stop, count):
        # Default values
        self.year = int(year)
        self.month = int(month)
        self.day = int(day)
        self.sheet = sheet
        self.route = route
        self.driver = driver
        self.schedule = schedule
        self.license = veh_license
        self.on_stop = on_stop
        self.off_stop = off_stop
        # Processing functions
        self.set_date()
        self.set_time(time)
        self.set_count(count)
        self.set_id()
        self.append_record()
        # Add record to the date it pertains
        Day.add_count(self.date, self.dow, self.week, self.count)

    def set_date(self):
        self.datestr = (str(self.year) + '/' + str(self.month) + '/' +
                         str(self.day))
        self.date = datetime.date(self.year, self.month, self.day)
        self.week = (str(self.date.isocalendar()[0]) + '_' +
                      str(self.date.isocalendar()[1]))
        self.dow = str(self.date.isocalendar()[2])
        return True

    def set_time(self, time):
        time = re.sub(':', '', time)
        try:
            self.time = str(int(time[:-2])) + ':' + str(time[-2:])
        except:
            raise RidershipErrors.EntryError('A problem with a time entry occurred in {}. Consult '.format(self.file) +
                                             ' records where boarding={} and deboarding={}'.format(self.on_stop,
                                                                                                   self.off_stop))
        return True

    def set_count(self, count):
        try:
            self.count = int(count)
        except:
            raise RidershipErrors.EntryError('A problem with a count entry occurred in {}. Consult '.format(self.file) +
                                             ' records where boarding={} and deboarding={}'.format(self.on_stop,
                                                                                                   self.off_stop))
        return True

    def set_id(self):
        self.ID = hex(Record.ID_generator)
        Record.ID_generator += 1
        Record.objects[self.ID] = self
        return True

    def append_record(self):
        Record.matrix.append([self.ID, self.year, self.month, self.day,
                              self.dow, self.sheet, self.route,
                              self.driver, self.schedule, self.license,
                              self.time, self.on_stop, self.off_stop,
                              self.count])
        return True

    @staticmethod
    def publish_matrix():
        if not os.path.exists(PATH + '/reports/ridership'):
            os.makedirs(PATH + '/reports/ridership')
        writer = csv.writer(open(PATH + '/reports/ridership/records.csv', 'w', newline=''),
                            delimiter=',', quotechar='|')
        for row in Record.matrix:
            writer.writerow(row)
        return True
    

class Day(object):

    objects = {}

    def __init__(self, year, month, day, date, week, dow):
        self.year = year
        self.month = month
        self.day = day
        self.date = date
        self.week = week
        self.dow = dow
        self.count = 0
        self.average = 0
        self.straight_line = INCREMENT * abs(date - BEGIN).days + BASELINE
        self.set_week()
        self.set_month()
        Day.objects[(year, month, day)] = self

    @staticmethod
    def add_count(date, dow, week, count):
        if (date.year, date.month, date.day) not in Day.objects:
            Day(date.year, date.month, date.day, date, week, dow)
        Day.objects[(date.year, date.month, date.day)].count += count
        return True

    def set_week(self):
        if self.week not in Week.objects:
            Week(self.week)
        Week.objects[self.week].days[self.dow] = self
        return True

    def set_month(self):
        month_key = str(self.year) + '_' + Month.convert_m[int(self.month)]
        if month_key not in Month.objects:
            Month(month_key)
        Month.objects[month_key].days[self.date] = self


class Week(object):

    objects = {}
    convert_d = {'Sunday': 0, 'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4, 'Friday': 5, 'Saturday': 6}
    convert_a = {0: 'Sunday', 1: 'Monday', 2: 'Tuesday', 3: 'Wedesday', 4: 'Thursday', 5: 'Friday', 6: 'Saturday',
                 7: 'Sunday'}

    def __init__(self, week):
        self.week = week
        self.days = {}
        Week.objects[week] = self

    @staticmethod
    def publish():
        if not os.path.exists(PATH + '/reports/ridership/weekly/excel'):
            os.makedirs(PATH + '/reports/ridership/weekly/excel')

        for week in sorted(Week.objects.keys()):
            # Open workbook and worksheet
            workbook = xlsxwriter.Workbook(PATH + '/reports/ridership/weekly/excel/' + str(week) + '.xlsx')
            worksheet = workbook.add_worksheet('Ridership')
            chart = workbook.add_chart({'type': 'column'})

            # Set week object and averages
            obj = Week.objects[week]
            obj.set_averages()

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
            for dow in sorted(obj.days.keys()):
                worksheet.write_row('A' + str(row),
                    [obj.days[dow].date.strftime('%A'),
                     obj.days[dow].date.strftime('%d, %b %Y'),
                     obj.days[dow].count, round(obj.days[dow].average, 2),
                     round(obj.days[dow].straight_line, 2)])
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
            chart.set_title({'name': 'Weekly Ridership'})
            chart.set_x_axis({'name': 'Day'})
            chart.set_y_axis({'name': 'Riders'})

            # Insert chart into the worksheet
            worksheet.insert_chart('A' + str(row + 2), chart, {'x_offset': 10, 'y_offset': 10})
            workbook.close()
        return True

    def set_averages(self):
        N = {}
        for week in sorted(Week.objects.keys()):
            if week == self.week:
                break
            for dow in Week.objects[week].days:
                try:
                    self.days[dow].average += Week.objects[week].days[dow].count
                    N[dow] = N.get(dow, 0) + 1
                except KeyError:
                    pass
        for dow in sorted(self.days.keys()):
            try:
                self.days[dow].average = self.days.get(dow, 0).average / float(N[dow])
            except:
                pass
        return True


class Month(object):

    objects = {}
    convert_m = {1: 'JAN', 2: 'FEB', 3: 'MAR', 4: 'APR', 5: 'MAY', 6: 'JUN', 7: 'JUL', 8: 'AUG', 9: 'SEP', 10: 'OCT',
                 11: 'NOV', 12: 'DEC'}

    def __init__(self, month):
        self.month = month
        self.days = {}
        Month.objects[month] = self

    @staticmethod
    def publish():
        if not os.path.exists(PATH + '/reports/ridership/monthly/excel'):
            os.makedirs(PATH + '/reports/ridership/monthly/excel')
        for month in sorted(Month.objects.keys()):
            writer = csv.writer(open(PATH + '/reports/ridership/monthly/excel/' + str(month) + '.csv', 'w', newline=''),
                                delimiter=',', quotechar='|')
            obj = Month.objects[month]
            for date in sorted(obj.days.keys()):
                writer.writerow([Week.convert_a[int(obj.days[date].dow)], date, obj.days[date].count,
                                 obj.days[date].average, obj.days[date].straight_line])
        return True


class Report(object):

    @staticmethod
    def prepare(features, start, end):
        # If no features, return total only
        if not features:
            count = 0
            for record in Record.objects:
                count += Record.objects[record].count
            return {'Total': count}

        # If features, produce variable data structure
        data = {}
        for record in Record.objects:
            obj = Record.objects[record]

            # If outside of the daterange, continue
            if obj.date < start or obj.date > end:
                continue

            # If inside the daterange, process count information
            i = 0
            DS = 'data'

            # Process all except the last feature
            while i < (len(features) - 1):
                try:
                    if eval('obj.' + features[i]) not in eval(DS):
                        exec(DS + '[\'' + eval('obj.' + features[i]) + '\']={}')
                    DS += '[\'' + eval('obj.' + features[i]) + '\']'
                except TypeError:
                    if eval('obj.' + features[i]) not in eval(DS):
                        exec(DS + '[' + str(eval('obj.' + features[i])) + ']={}')
                    DS += '[' + str(eval('obj.' + features[i])) + ']'
                i += 1

            # Process the counts of the last feature
            try:
                exec(DS + '[\'' + eval('obj.' + features[-1]) + '\']=' + DS + '.get(\'' + eval('obj.' + features[-1]) +
                     '\', 0) + obj.count')
            # Except if boolean
            except TypeError:
                exec(DS + '[' + str(eval('obj.' + features[-1])) + ']=' + DS + '.get(' +
                     str(eval('obj.' + features[-1])) + ', 0) + obj.count')
        return data

    @staticmethod
    def dict_to_matrix(data):
        # Set outer and inner keys
        outer_keys = sorted(data.keys())
        inner_keys_D = {}
        # Find all inner key values
        for o_key in outer_keys:
            for i_key in data[o_key]:
                inner_keys_D[i_key] = True
        inner_keys = sorted(inner_keys_D.keys())
        # Set matrix
        matrix = [[''] + inner_keys]
        for o_key in outer_keys:
            row = [o_key]
            for i_key in inner_keys:
                # If inner key is found for the outer key, set amount
                if i_key in data[o_key]:
                    row.append(data[o_key][i_key])
                # Otherwise inner key DNE for outer key, set to 0
                else:
                    row.append(0)
            matrix.append(row)
        return matrix

    @staticmethod
    def recurse_data(data, features, writer, prev=[], i=0, limit=2):
        if i == (len(features) - limit):
            matrix = Report.dict_to_matrix(data)
            # Write title by previous values
            writer.writerow(prev)
            # Write matrix rows
            for row in matrix:
                writer.writerow(row)
            # Write empty row
            writer.writerow([])
        else:
            for key in sorted(data.keys()):
                Report.recurse_data(data[key], features, writer, prev + [str(features[i]).title() + ': ' + str(key)],
                                     i+1, limit=limit)
        return True

    @staticmethod
    def generate(features, start=datetime.date(2015, 8, 31), end=datetime.date.today()):
        data = Report.prepare(features, start, end)
        if not os.path.isdir(PATH + '/reports/ridership/custom'):
            os.makedirs(PATH + '/reports/ridership/custom')
        writer = csv.writer(open(PATH + '/reports/ridership/custom/Ridership_' + '_'.join(features).title() +
                                 '.csv', 'w', newline=''), delimiter=',', quotechar='|')
        Report.recurse_data(data, features, writer)
        return True


def publish():
    # Records
    Record.publish_matrix()
    # Weekly
    Week.publish()
    # Monthly
    Month.publish()
    return True


Sheet.process()

if __name__ == "__main__":
    publish()

    start = datetime.date(2015, 8, 31)
    end = datetime.date(2016, 12, 31)

    Report.generate(['week', 'route'], start=start, end=end)
    Report.generate(['year', 'month', 'route'], start=start, end=end)
    Report.generate(['week', 'dow'], start=start, end=end)
    Report.generate(['dow', 'on_stop', 'off_stop'], start=start, end=end)
    Report.generate(['year', 'month', 'day', 'route'], start=start, end=end)
    Report.generate(['on_stop', 'off_stop'], start=start, end=end)
    Report.generate(['time', 'route'], start=start, end=end)
