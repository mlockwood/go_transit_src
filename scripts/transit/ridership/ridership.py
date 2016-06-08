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
import src.scripts.transit.route.route as rt
import src.scripts.transit.ridership.errors as RidershipErrors

# Classes and variables from src
from src.scripts.transit.constants import PATH, BEGIN, BASELINE, INCREMENT
from src.scripts.transit.ridership.constants import HEADER, STANDARD, ORDER, META_MAP
from src.scripts.utils.functions import csv_writer


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
    rewrite = {}
    errors = []
    warnings = []

    def __init__(self, file):
        self.file = file
        self.time_key = 0
        self.records = {}
        self.entries = []
        self.temp = {}
        self.meta = {}
        self.errors = []
        self.warnings = []
        self.strp = None
        self.date = None
        self.dow = None
        Sheet.objects[self.file] = self

    @staticmethod
    def process():
        # obj_list = []

        for dirpath, dirnames, filenames in os.walk(PATH + '/data/ridership'):
            if 'archive' in dirpath or 'archive' in dirnames:
                continue
            for filename in [f for f in filenames if re.search('\d{6}[_|\-]S\d+[A-Z]?\.csv', f)]:
                obj = Sheet((str(dirpath) + '/' + str(filename)))
                try:
                    output = obj.read_sheet()
                except Exception as e:
                    print('{} cannot be read due to: {}'.format(filename, e))
                Sheet.errors += output[0]
                Sheet.warnings += output[1]

        """
        # This section is not working, it is attempting to multithread the
        # reading of the datasheets but has pickling problems due to the use
        # of objects.
        pool = mp.Pool()
        results = pool.map_async(Sheet.read_sheet, obj_list)
        """

        csv_writer('{}/reports/ridership/'.format(PATH), 'errors', Sheet.errors)
        csv_writer('{}/reports/ridership/'.format(PATH), 'warnings', Sheet.warnings)

        return True

    def convert_messages(self, messages):
        temp = []
        for message in messages:
            temp.append([self.file] + list(message))
        return temp

    def overwrite(self):
        print('File {} was overwritten.'.format(self.file))
        writer = csv.writer(open(self.file, 'w', newline=''), delimiter=',', quotechar='|')
        writer.writerow(['METADATA'])
        for i in sorted(ORDER.keys()):
            writer.writerow([str(ORDER[i]).title(), self.meta[ORDER[i]]])

        writer.writerow([])
        writer.writerow(['DATA'])
        writer.writerow(HEADER)
        for row in self.entries:
            writer.writerow(row)
        return True

    def overwrite_route(self):
        prev = self.meta['route']

        # 2015 AUG 31 to 2015 NOV 8
        if self.date < datetime.datetime(2015, 11, 9):
            self.meta['route'] = '1'

        # 2015 NOV 9 to 2015 DEC 15
        if datetime.datetime(2015, 11, 9) <= self.date < datetime.datetime(2015, 12, 16):
            # Weekends are Route 1 only
            if self.dow == '6' or self.dow == '7':
                self.meta['route'] = '1'
            # Weekdays are 1&2
            else:
                self.meta['route'] = '1&2'

        # 2015 DEC 15 to 2016 JAN 15
        if datetime.datetime(2015, 12, 16) <= self.date < datetime.datetime(2016, 1, 16):
            # Weekends are Route 1 only
            if self.dow == '6' or self.dow == '7':
                self.meta['route'] = '1'
            # Weekdays
            else:
                # Early morning Route 2 service only
                if int(re.sub(':', '', self.meta['end_shift'])) <= 700:
                    self.meta['route'] = '2'
                # Otherwise Routes 1&2
                else:
                    self.meta['route'] = '1&2'

        # 2016 JAN 16 to 2016 MAR 27
        if datetime.datetime(2016, 1, 16) <= self.date < datetime.datetime(2016, 3, 28):
            # Weekends are Route 10 only
            if self.dow == '6' or self.dow == '7':
                self.meta['route'] = '10'
            # Weekdays
            else:
                # Early morning Route 2 service only
                if int(re.sub(':', '', self.meta['end_shift'])) <= 700 or self.meta['sheet'].lower() == 's5z':
                    self.meta['route'] = '2'
                # Otherwise Routes 1&2
                else:
                    self.meta['route'] = '1&2'

        # 2016 MAR 28 to 2016 APR 24
        if datetime.datetime(2016, 3, 28) <= self.date < datetime.datetime(2016, 4, 25):
            # Weekends are Routes 10&20
            if self.dow == '6' or self.dow == '7':
                self.meta['route'] = '10&20'
            # Weekdays
            else:
                # Early morning Route 2 service only
                if int(re.sub(':', '', self.meta['end_shift'])) <= 700 or self.meta['sheet'].lower() == 's5z':
                    self.meta['route'] = '2'
                # Otherwise Routes 1&2
                else:
                    self.meta['route'] = '1&2'

        if self.meta['route'] == prev:
            return False
        else:
            return True

    def read_sheet(self):
        reader = csv.reader(open(self.file, 'r', newline='', encoding="utf8"), delimiter=',', quotechar='|')
        meta = False
        data = False

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
                # if cur_meta not in Sheet.delete
                self.meta[cur_meta] = cur_value
                        
            # Data
            if data:
                if row != HEADER:
                    self.entries.append(row)

        # Validation
        self.validate()

        # Actually process record using the latest version methodology
        self.set_records()

        # Send error and warning messages to report
        return self.convert_messages(self.errors), self.convert_messages(self.warnings)

    def validate(self):
        # If no data, alert user just in case of error
        if not self.entries:
            self.warnings += [RidershipErrors.EmptyDataWarning.get()]

        # Check if the naming convention matches the standard
        match = re.search('\d{6}', self.file)
        if not match:
            self.warnings += [RidershipErrors.NamingConventionWarning.get()]

        # Build date strp such as '20160831' from metadata
        self.strp = '{}{:02d}{:02d}'.format(int(self.meta['year']), int(self.meta['month']), int(self.meta['day']))
        self.date = datetime.datetime.strptime(self.strp, '%Y%m%d')
        self.dow = str(self.date.isocalendar()[2])

        # Construct date strp from file name
        f_year = '20' + self.file[match.span()[0]:match.span()[0] + 2]
        f_month = self.file[match.span()[0] + 2:match.span()[0] + 4]
        f_day = self.file[match.span()[0] + 4:match.span()[0] + 6]

        # Check if the file name matches the year, month, and day file contents
        if self.strp != '{}{}{}'.format(f_year, f_month, f_day):
            self.warnings += [RidershipErrors.FileNameMismatchWarning.get()]

        # Add standard metadata variables to those missing from the version template
        for meta in STANDARD:
            if meta not in self.meta:
                self.meta[meta] = STANDARD[meta][0]
                if STANDARD[meta][1] == 'r':
                    self.errors += [RidershipErrors.MissingMetadataError.get(meta)]

        # Overwrite metadata
        if self.overwrite_route():
            self.overwrite()

        return True

    def set_records(self):
        r = 1
        new_entries = []
        for entry in self.entries:
            # Ignore blank rows and counts of 0
            if not re.sub(' ', '', ''.join(str(x) for x in entry)):
                continue
            elif entry[2] == '0':
                continue

            # Validate that every column has been completed for the record
            i = 0
            while i < len(entry):
                if not re.sub(' ', '', entry[i]):
                    self.errors += [RidershipErrors.EntryError.get(r, HEADER[i])]
                i += 1
            
            # Stop validation and mapping
            # Boarding (on)
            try:
                on = st.Stop.obj_map[entry[0]].stop_id
            except KeyError:
                self.errors += [RidershipErrors.StopValidationError.get('Boarding', entry[0], r)]
                on = '0'

            # Deboarding (off)
            try:
                off = st.Stop.obj_map[entry[3]].stop_id
            except KeyError:
                self.errors += [RidershipErrors.StopValidationError.get('Deboarding', entry[3], r)]
                off = '0'

            # Time validation
            time = re.sub(':', '', entry[1])
            if len(time) > 4:
                self.errors += [RidershipErrors.TimeValidationError.get(time, r)]
                time = 'xxxx'
            else:
                try:
                    time = str(int(time[:-2])) + ':' + str(time[-2:])
                except TypeError:
                    self.errors += [RidershipErrors.TimeValidationError.get(time, r)]
                    time = 'xxxx'
                except ValueError:
                    if len(time) == 2:
                        time = '00:{}'.format(time)
                    elif len(time) == 1:
                        time = '00:0{}'.format(time)
                    else:
                        self.errors += [RidershipErrors.TimeValidationError.get(time, r)]
                        time = 'xxxx'

            # Count validation
            try:
                count = int(entry[2])
            except TypeError:
                self.errors += [RidershipErrors.CountValidationError.get(entry[2], r)]
                count = 0

            # Set record
            record = Record(self.file, self.meta['year'], self.meta['month'], self.meta['day'], self.meta['sheet'],
                            self.meta['route'], self.meta['driver'], self.meta['schedule'], self.meta['license'],
                            on, off, time, count)
            self.records[(on, off, time)] = record
            #  new_entries += [[on, re.sub(':', '', time), count, off]]
            r += 1

        """
        # Write new file to update changes
        if self.entries != new_entries:
            self.entries = new_entries
            self.overwrite()
        """
        return True


class Record(object):

    objects = {}
    ID_generator = 1
    matrix_header = ['ID', 'Year', 'Month', 'Day', 'Weekday', 'Sheet', 'Route', 'On_Route', 'Off_Route', 'Driver',
                     'Schedule', 'License', 'Time', 'On_Stop', 'Off_Stop', 'Count']
    matrix = [matrix_header]

    def __init__(self, file, year, month, day, sheet, route, driver, schedule, veh_license, on_stop, off_stop, time,
                 count):
        # Default values
        self.file = file
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
        self.time = time
        self.count = count

        # Processing attributes
        self.datestr = '{}/{}/{}'.format(*[str(s) for s in [self.year, self.month, self.day]])
        self.date = datetime.datetime(self.year, self.month, self.day)
        self.week = Week.get_name(self.date)
        self.dow = str(self.date.isocalendar()[2])

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
        Day.add_count(self.date, self.dow, self.week, self.count)

    def get_pseudo(self, stop):
        if str(stop) in ['100', '300']:
            return None

        elif re.sub('[A-Za-z]', '', self.schedule) in ['8', '9']:
            return 'Evening'

        elif self.sheet.lower() == 's5z':
            return 'Morning'

        elif self.date >= datetime.datetime(2016, 4, 25) and self.sheet.lower() == 's5a':
            return 'Morning'

        else:
            routes = re.split('&', self.route)
            for route_id in routes:
                route = rt.Route.objects[route_id]
                for sheet in route.sheets:
                    for stop_id in sheet.stops:
                        if str(stop) == str(stop_id):
                            return route_id

        if self.date >= datetime.datetime(2016, 4, 25):
            Sheet.errors += [[self.file] + list(RidershipErrors.StopUnavailableForRouteError.get(stop, self.route))]
        return 'Unmatched'

    def append_record(self):
        Record.matrix.append([self.ID, self.year, self.month, self.day, self.dow, self.sheet, self.route,
                              self.on_pseudo, self.off_pseudo, self.driver, self.schedule, self.license, self.time,
                              self.on_stop, self.off_stop, self.count])
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
        month_key = '{}_{}_{}'.format(str(self.year), str(self.month), Month.convert_m[int(self.month)])
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
    def get_name(date):
        if len(str(date.isocalendar()[1])) == 1:
            return '{}_0{}'.format(str(date.isocalendar()[0]), str(date.isocalendar()[1]))
        else:
            return '{}_{}'.format(str(date.isocalendar()[0]), str(date.isocalendar()[1]))

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


def publish():
    # Records
    Record.publish_matrix()
    # Weekly
    Week.publish()
    # Monthly
    Month.publish()
    return True


if __name__ == "__main__":
    Sheet.process()

    publish()
