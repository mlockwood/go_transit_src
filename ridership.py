
import configparser
import csv
import datetime
import os
import re
import sys
import xlsxwriter

import multiprocessing as mp

"""
Closed Classes----------------------------------------------------------
"""
class PathSetter:

    def set_pythonpath(directory='', subdirectory=''):
        if directory:
            directory = PathSetter.find_path(directory)
            if subdirectory:
                if directory[-1] != '/' and subdirectory[0] != '/':
                    directory += '/'
                directory += subdirectory
        else:
            directory = os.getcwd()
        sys.path.append(directory)
        return True

    def find_path(directory):
        match = re.search('/|\\' + str(directory), os.getcwd())
        if not match:
            raise IOError(str(directory) + 'is not in current working ' +
                          'directory')
        return os.getcwd()[:match.span()[0]] + '/' + directory

"""
GO Transit Imports------------------------------------------------------
"""
PathSetter.set_pythonpath()
import stops as st

"""
Main Classes------------------------------------------------------------
"""
class System:

    begin = datetime.date(2015, 8, 31)
    finish = datetime.date(2016, 11, 30)
    baseline = 19.4000
    final = 83.3333
    increment = (final - baseline) / abs(finish - begin).days
    go_transit_path = PathSetter.find_path('go_transit')

class Sheet:

    objects = {}
    structure = {}
    sheet_names = {}
    rewrite = {}
    version_1 = datetime.date(2015, 8, 31)
    version_2 = datetime.date(2015, 9, 8)
    version_3 = datetime.date(2015, 11, 1)
    header = ['Boarding', 'Time', 'Count', 'Destination']
    pvn = '3' # standard previous version number for files

    def __init__(self, file):
        self._file = file
        self._pvn = Sheet.pvn
        self._start_shift = ''
        self._time_key = 0
        self._records = {}
        self._entries = []
        self._temp = {}
        Sheet.objects[(self._file)] = self

    @staticmethod
    def process():
        Sheet.load_config()
        # obj_list = []
        for dirpath, dirnames, filenames in os.walk(System.go_transit_path
                                                    + '/data'):
            for filename in [f for f in filenames if re.search(
                '\d{6}_S\d', f)]:
                obj = Sheet((str(dirpath) + '/' + str(filename)))
                obj.read_sheet()
        """
        # This section is not working, it is attempting to multithread the
        # reading of the datasheets but has pickling problems due to the use
        # of objects.
        pool = mp.Pool()
        results = pool.map_async(Sheet.read_sheet, obj_list)
        """
        Sheet.write_sheets()
        return True

    @staticmethod
    def load_config():
        config = configparser.ConfigParser()
        config.read('sheet.ini')
        Sheet.standard = config['STANDARD']
        Sheet.metadata = config['METADATA']
        Sheet.override = config['OVERRIDE']
        Sheet.delete = config['DELETE']
        Sheet.order = {int(k):v for k,v in config['ORDER'].items()}
        Sheet.index = int(config['INDEX']['sheet'])
        if 'version' in Sheet.override:
            Sheet.pvn = Sheet.override['version']
        Sheet.obs_map = {}
        for meta in Sheet.metadata:
            prev_list = re.split(',', Sheet.metadata[meta])
            for prev in prev_list:
                Sheet.obs_map[prev] = meta
        return True

    @staticmethod
    def write_sheets():
        # Define sheet names
        chars = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']
        for date in Sheet.structure:
            for schedule in Sheet.structure[date]:
                i = 0
                for time in sorted(Sheet.structure[date][schedule].keys()):
                    if time == 0:
                        print('Please examine the time for', date,
                              'for all sheets with a schedule of', schedule)
                    Sheet.sheet_names[(date[0], date[1], date[2], schedule,
                                       time)] = 'S' + str(schedule) + chars[i]
                    i += 1

        # Write each sheet to file
        for obj in Sheet.rewrite:
            obj._sheet = Sheet.sheet_names[(obj._year, obj._month, obj._day,
                                            obj._schedule, obj._time_key)]
            writer = obj.set_writer()
            writer.writerow(['METADATA'])
            obj._meta_L[Sheet.index][1] = obj._sheet
            for row in obj._meta_L:
                writer.writerow(row)
            writer.writerow([])
            writer.writerow(['DATA'])
            writer.writerow(['Boarding', 'Time', 'Count', 'Destination'])
            for entry in obj._entries:
                writer.writerow(entry)
        return True

    def set_writer(self):
        date = datetime.datetime(int(self._year), int(self._month),
                                 int(self._day))
        directory = (System.go_transit_path + '/formatted/' +
            date.strftime('%Y_%m') + '/' + date.strftime('%y%m%d'))
        if not os.path.exists(directory):
            os.makedirs(directory)
        writer = csv.writer(open(directory + '/' + date.strftime('%y%m%d') +
            '_' + self._sheet + '.csv', 'w', newline=''), delimiter=',',
            quotechar='|')
        return writer

    def read_sheet(self):
        reader = csv.reader(open(self._file, 'r', newline=''),
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
            # Columns boolean handle
            elif row[0] == 'COLUMNS':
                columns = True
                meta = False
                continue
            # Data boolean handle
            elif row[0] == 'DATA':
                data = True
                columns = False
                meta = False
                continue
            # </Handle Types>
            
            # Metadata
            if meta == True:
                # Handle metadata category
                cur_meta = str(row[0]).lower()
                if cur_meta not in Sheet.standard:
                    if cur_meta in Sheet.obs_map:
                        cur_meta = Sheet.obs_map[cur_meta]
                    elif cur_meta not in Sheet.delete:
                        print(cur_meta + ' in ' + str(self._file) +
                              ' cannot be mapped.')
                # Handle metadata value
                cur_value = str(row[1])
                if cur_meta in Sheet.override:
                    if cur_meta == 'version':
                        self._pvn = cur_value
                    cur_value = Sheet.override[cur_meta]
                # Add meta category, value to meta_D and Sheet object
                if cur_meta not in Sheet.delete:
                    meta_D[cur_meta] = cur_value
                try:
                    exec('self._' + cur_meta + '=\'' + cur_value + '\'')
                except:
                    raise ValueError('Metadata error in ' + cur_value)
            
            # Columns (for older versions)
            if columns == True:
                i = 3
                while i < len(row):
                    exec('self._' + str(row[0]).lower() + '_' + str(i) +'=\'' +
                         str(row[i]) + '\'')
                    if (not self._start_shift and not self._time_key and
                        row[0].lower() != 'start'):
                        try:
                            self._time_key = int(re.sub(':', '', row[i]))
                        except:
                            pass
                    i += 1
                        
            # Data
            if data == True:
                # Version 3
                if self._pvn == '3':
                    if row != Sheet.header:
                        self._entries.append(row)
                # Versions 1 and 2
                elif self._pvn == '2' or self._pvn == '1':
                    direction = self.set_1_and_2_records(row, direction)
                # If there is an unrecognized Version value alert the user
                else:
                    raise ValueError('Version not recognized for ' +
                                     str(self._file))
        
        # Add sheet to the general sheet structure
        if not (self._year, self._month, self._day) in Sheet.structure:
            Sheet.structure[(self._year, self._month, self._day)] = {}
        if self._schedule not in Sheet.structure[(self._year, self._month,
                                                  self._day)]:
            Sheet.structure[(self._year, self._month, self._day)][
                self._schedule] = {}
        if self._start_shift:
            Sheet.structure[(self._year, self._month, self._day)][
                self._schedule][int(re.sub(':', '', self._start_shift))] = True
            self._time_key = int(re.sub(':', '', self._start_shift))
        else:
            Sheet.structure[(self._year, self._month, self._day)][
                self._schedule][self._time_key] = True
        
        # If no data, alert user just in case of error
        if data == False:
            print(self._file, 'does not contain any data.')
        # Convert on/off records to single records
        if self._pvn == '2' or self._pvn == '1':
            self.upversion_1_and_2()
        # Final metadata check -- for completeness
        for category in Sheet.standard:
            if category not in meta_D:
                meta_D[category] = Sheet.standard[category]
                exec('self._' + category + '=' + Sheet.standard[category])
        # Actually process record using the latest version methodology
        self.set_records()

        # Rewrite files of lower versions
        if self._pvn == '2' or self._pvn == '1' or self._pvn == '3':
            # Convert metadata Dictionary to ordered List
            self._meta_L = []
            for index in sorted(Sheet.order.keys()):
                if Sheet.order[index] in meta_D:
                    self._meta_L.append([Sheet.order[index].title(),
                                         meta_D[Sheet.order[index]]])
            # Send to have file rewritten
            Sheet.rewrite[self] = True
        return True

    def set_records(self):
        for entry in self._entries:
            # General record validation
            if entry == Sheet.header:
                continue
            if entry[2] == '0':
                continue
            if not re.sub(' ', '', ''.join(str(x) for x in entry)):
                continue
            i = 0
            while i < len(entry):
                if not entry[i]:
                    raise ValueError(self._file + ' does not have a ' +
                                     Sheet.header[i])
                i += 1
            
            # Stop validation and mapping
            # Boarding (on)
            if str(entry[0]).lower() in st.Stop.obj_map:
                on = st.Stop.obj_map[str(entry[0]).lower()]._stop_id
            else:
                raise ValueError('Stop ' + str(entry[0]) + ' from file ' +
                                 str(self._file) + ' is not recognized.')
            # Deboarding (Off)
            if str(entry[3]).lower() in st.Stop.obj_map:
                off = st.Stop.obj_map[str(entry[3]).lower()]._stop_id
            else:
                raise ValueError('Stop ' + str(entry[3]) + ' from file ' +
                                 str(self._file) + ' is not recognized.')
            
            # Set record
            record = Record(self._year, self._month, self._day, self._sheet,
                            entry[0][0], self._driver, self._schedule,
                            entry[1], '', entry[0], 'On', entry[2])
            self._records[(entry[1], 'On', entry[1])] = record
            record = Record(self._year, self._month, self._day, self._sheet,
                            entry[3][0], self._driver, self._schedule,
                            entry[1], '', entry[3], 'Off', entry[2])
            self._records[(entry[3], 'Off', entry[1])] = record
        return True

    def set_1_and_2_records(self, row, direction):
        if row[0] == 'Return':
            direction = '2'
            return direction
        i = 3
        while i < len(row):
            if re.sub(' ', '', row[i]):
                # Set time base
                # Version 2 time
                if self._pvn == '2':
                    if direction == '1':
                        time = eval('self._depart_' +
                            self._direction_2[-2:].lower() + '_' + str(i))
                        if (i == 3 and self._start_3 == '1J' and not
                            self._depart_mh_3):
                            if self._schedule == '3':
                                time = '640'
                    elif direction == '2':
                        time = eval('self._depart_' +
                            self._direction_1[-2:].lower() + '_' + str(i))
                        if (i == 3 and self._start_3 == '1J' and not
                            self._depart_wz_3):
                            if self._schedule == '2':
                                time = '650'
                            elif self._schedule == '3':
                                time = '710'
                # Version 1 time
                elif self._pvn == '1':
                    time = eval('self._time_' + str(i))
                # Modify time to actual stop
                time = re.sub(':', '', time)
                dt = datetime.datetime(int(self._year), int(self._month),
                    int(self._day), int(time[:-2]), int(time[-2:]))
                if self._version == '1' and direction == '2':
                    dt = dt + datetime.timedelta(0, 60 * 30)
                time = dt + datetime.timedelta(0, 60 * int(eval(
                    'st.Stop.obj_map[row[1].lower()]._historic_time_' +
                    str(direction))))
                # Add (time, on|off) to temp with [stop, count]
                self._temp[(time.strftime('%H%M'), row[2])] = [row[1],
                                                               int(row[i])]
            i += 1
        return direction

    def upversion_1_and_2(self):
        stack = {}
        cur_key = 0
        new_key = 0
        final = {}
        # record is (time, on|off)
        for entry in sorted(self._temp.keys()):
            if entry[1] == 'On':
                # stack is [on_stop, time, count]
                stack[new_key] = [self._temp[entry][0], entry[0],
                                  self._temp[entry][1]]
                new_key += 1
            elif entry[1] == 'Off':
                # final is (on_stop, time, count, off_stop) = True
                count = self._temp[entry][1]
                while count > 0:
                    if stack[cur_key][2] > count:
                        final[(stack[cur_key][0], stack[cur_key][1], count,
                               self._temp[entry][0])] = True
                        stack[cur_key][2] -= count
                        count = 0
                    else:
                        final[(stack[cur_key][0], stack[cur_key][1],
                            stack[cur_key][2], self._temp[entry][0])
                            ] = True
                        count -= stack[cur_key][2]
                        del stack[cur_key]
                        cur_key += 1
        for entry in sorted(final.keys(), key=lambda x:x[1]):
            self._entries.append(list(entry))
        return True

    def check_metadata(self):
        # Update! Make values dependent on version
        values = ['sheet', 'version', 'driver', 'year', 'month', 'day',
                  'schedule', 'mileage_start', 'mileage_end', 'mileage_total']
        for value in values:
            try:
                eval('self._' + value)
            except:
                raise AttributeError(self._file + ' is missing ' + value)
        return True
                            
class Record:

    objects = {}
    ID_generator = 1

    def __init__(self, year, month, day, sheet, route, driver, vehicle, time,
                 direction, stop, entry, count):
        self._year = int(year)
        self._month = int(month)
        self._day = int(day)
        self._sheet = sheet
        self._route = route
        self._driver = driver
        time = re.sub(':', '', time)
        try:
            self._time = str(int(time[:-2])) + ':' + str(time[-2:])
        except:
            print(year, month, day, sheet, stop)
        self._direction = direction
        self._stop = stop
        self._entry = entry
        self._date = datetime.date(int(year), int(month), int(day))
        self._week = (str(self._date.isocalendar()[0]) + '_' +
                      str(self._date.isocalendar()[1]))
        self._dow = str(self._date.isocalendar()[2])
        try:
            self._count = int(count)
        except:
            print(year, month, day, sheet, stop, count)
        Day.add_count(self._date, self._dow, self._week, self._count)
        self._ID = hex(Record.ID_generator)
        Record.ID_generator += 1
        Record.objects[self._ID] = self

class Day:

    objects = {}

    def __init__(self, year, month, day, date, week, dow):
        self._year = year
        self._month = month
        self._day = day
        self._date = date
        self._week = week
        self._dow = dow
        self._count = 0
        self._average = 0
        self._straight_line = System.increment * abs(date - System.begin
                                                     ).days + System.baseline
        self.set_week()
        self.set_month()
        Day.objects[(year, month, day)] = self

    @staticmethod
    def add_count(date, dow, week, count):
        if (date.year, date.month, date.day) not in Day.objects:
            Day(date.year, date.month, date.day, date, week, dow)
        Day.objects[(date.year, date.month, date.day)]._count += (count / 2.0)
        return True

    def set_week(self):
        if self._week not in Week.objects:
            Week(self._week)
        Week.objects[self._week]._days[self._dow] = self
        return True

    def set_month(self):
        month_key = str(self._year) + '_' + str(self._month)
        if month_key not in Month.objects:
            Month(month_key)
        Month.objects[month_key]._days[self._date] = self

class Week:

    objects = {}
    convert_d = {'Sunday': 0, 'Monday': 1, 'Tuesday': 2, 'Wednesday': 3,
               'Thursday': 4, 'Friday': 5, 'Saturday': 6}
    convert_a = {0: 'Sunday', 1: 'Monday', 2: 'Tuesday', 3: 'Wedesday',
                 4: 'Thursday', 5: 'Friday', 6: 'Saturday', 7: 'Sunday'}

    def __init__(self, week):
        self._week = week
        self._days = {}
        Week.objects[week] = self

    @staticmethod
    def publish():
        if not os.path.exists(System.go_transit_path +
                              '/reports/ridership/weekly/excel'):
            os.makedirs(System.go_transit_path +
                        '/reports/ridership/weekly/excel')
        for week in sorted(Week.objects.keys()):
            # Open workbook and worksheet
            workbook = xlsxwriter.Workbook(System.go_transit_path +
                '/reports/ridership/weekly/excel/' + str(week) + '.xlsx')
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
            worksheet.write_row('A1', ['Weekday', 'Date', 'Riders', 'Average',
                                       'Pilot Target'])
            # Write data
            row = 2
            for dow in sorted(obj._days.keys()):
                worksheet.write_row('A' + str(row),
                    [obj._days[dow]._date.strftime('%A'),
                     obj._days[dow]._date.strftime('%d, %b %Y'),
                     obj._days[dow]._count, round(obj._days[dow]._average, 2),
                     round(obj._days[dow]._straight_line, 2)])
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
            worksheet.insert_chart('A' + str(row + 2), chart, {'x_offset': 10,
                                                               'y_offset': 10})
            workbook.close()
        return True

    def set_averages(self):
        N = {}
        for week in sorted(Week.objects.keys()):
            if week == self._week:
                break
            for dow in Week.objects[week]._days:
                try:
                    self._days[dow]._average += Week.objects[
                        week]._days[dow]._count
                    N[dow] = N.get(dow, 0) + 1
                except KeyError:
                    pass
        for dow in sorted(self._days.keys()):
            try:
                self._days[dow]._average = self._days[dow]._average / float(
                    N[dow])
            except:
                pass
        return True

class Month:

    objects = {}

    def __init__(self, month):
        self._month = month
        self._days = {}
        Month.objects[month] = self

    @staticmethod
    def publish():
        if not os.path.exists(System.go_transit_path +
                              '/reports/ridership/monthly/excel'):
            os.makedirs(System.go_transit_path +
                        '/reports/ridership/monthly/excel')
        for month in sorted(Month.objects.keys()):
            writer = csv.writer(open(System.go_transit_path +
                '/reports/ridership/monthly/excel/' + str(month) + '.csv', 'w',
                newline=''), delimiter=',', quotechar='|')
            obj = Month.objects[month]
            for date in sorted(obj._days.keys()):
                writer.writerow([Week.convert_a[int(obj._days[date]._dow)],
                    date, obj._days[date]._count, obj._days[date]._average,
                    obj._days[date]._straight_line])
        return True

class Report:

    @staticmethod
    def _prepare(features, start, end):
        # If no features, return total only
        if not features:
            count = 0
            for record in Record.objects:
                count += Record.objects[record]._count
            return {'Total': count}
        # If features, produce variable data structure
        data = {}
        for record in Record.objects:
            obj = Record.objects[record]
            # If outside of the daterange, continue
            if obj._date < start or obj._date > end:
                continue
            # If inside the daterange, process count information
            i = 0
            DS = 'data'
            # Process all except the last feature
            while i < (len(features) - 1):
                try:
                    if eval('obj._' + features[i]) not in eval(DS):
                        exec(DS + '[\'' + eval('obj._' + features[i]) +
                             '\']={}')
                    DS += '[\'' + eval('obj._' + features[i]) + '\']'
                except TypeError:
                    if eval('obj._' + features[i]) not in eval(DS):
                        exec(DS + '[' + str(eval('obj._' + features[i])) +
                             ']={}')
                    DS += '[' + str(eval('obj._' + features[i])) + ']'
                i += 1
            # Process the counts of the last feature
            try:
                # If entry is a feature add the full object count
                if 'entry' in features:
                    exec(DS + '[\'' + eval('obj._' + features[-1]) + '\']=' +
                         DS + '.get(\'' + eval('obj._' + features[-1]) +
                         '\', 0) + obj._count')
                # If entry is not a feature add half the object count
                else:
                    exec(DS + '[\'' + eval('obj._' + features[-1]) + '\']=' +
                         DS + '.get(\'' + eval('obj._' + features[-1]) +
                         '\', 0) + (obj._count / 2.0)')
            # Except if boolean
            except TypeError:
                # If entry is a feature add the full object count
                if 'entry' in features:
                    exec(DS + '[' + str(eval('obj._' + features[-1])) + ']=' +
                         DS + '.get(' + str(eval('obj._' + features[-1])) +
                         ', 0) + obj._count')
                # If entry is not a feature add half the object count
                else:
                    exec(DS + '[' + str(eval('obj._' + features[-1])) + ']=' +
                         DS + '.get(' + str(eval('obj._' + features[-1])) +
                         ', 0) + (obj._count / 2.0)')
        return data

    @staticmethod
    def _dict_to_matrix(data):
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
    def _recurse_data(data, features, writer, prev=[], i=0,
                      limit=2):
        if i == (len(features) - limit):
            matrix = Report._dict_to_matrix(data)
            # Write title by previous values
            writer.writerow(prev)
            # Write matrix rows
            for row in matrix:
                writer.writerow(row)
            # Write empty row
            writer.writerow([])
        else:
            for key in sorted(data.keys()):
                Report._recurse_data(data[key], features, writer, prev + [
                                str(features[i]).title() + ': ' + str(key)],
                                     i+1, limit=limit)
        return True    

    @staticmethod
    def generate(features, start=datetime.date(2015, 8, 31),
                end=datetime.date.today()):
        data = Report._prepare(features, start, end)
        if not os.path.isdir(System.go_transit_path + '/reports/ridership'):
            os.makedirs(System.go_transit_path + '/reports/ridership')
        writer = csv.writer(open(System.go_transit_path +
            '/reports/ridership/Ridership_' + '_'.join(features).title() +
            '.csv', 'w', newline=''), delimiter=',', quotechar='|')
        Report._recurse_data(data, features, writer)
        return True

    @staticmethod
    def publish():
        # Weekly
        Week.publish()
        # Monthly
        Month.publish()
        return True

    @staticmethod
    def publish_mileage():
        data = {}
        for sheet in Sheet.objects:
            obj = Sheet.objects[sheet]
            data[(obj._year, obj._month, obj._day)] = data.get((obj._year,
                                                                obj._month,
                                                                obj._day), 0
                                            ) + float(obj._mileage_total)
        for key in sorted(data.keys()):
            print(key, data[key])
        
                        
"""
User Interface----------------------------------------------------------
"""
Sheet.process()

start = datetime.date(2015, 8, 31)
end = datetime.date(2016, 12, 31)

Report.publish()
Report.generate(['stop', 'entry'], start=start, end=end)
Report.generate(['dow', 'stop', 'entry'], start=start, end=end)
Report.generate(['week', 'route'], start=start, end=end)
Report.generate(['week', 'stop', 'entry'], start=start, end=end)
Report.generate(['year', 'month', 'day', 'route'], start=start, end=end)
Report.generate(['year', 'month', 'stop', 'entry'], start=start, end=end)
Report.generate(['year', 'month', 'day', 'stop', 'entry'], start=start, end=end)
#Report.publish_mileage()

