
import csv
import datetime
import os
import re
import xlsxwriter

"""
Closed Classes----------------------------------------------------------
"""

class Stop:

    objects = {}

    def __init__(self, ID, name, delay):
        self._ID = ID
        self._name = name
        self._delay = delay
        self._entry = {}
        self._exit = {}


class Route:

    objects = {}

    def __init__(self, name, depart, reverse, ):
        self._name = name
        self._stops = {}


class Driver:

    objects = {}

    def __init__(self, name):
        self._name = name
        self._stops = {}


class Vehicle:

    objects = {}

    def __init__(self, license_plate):
        self._license_plate = license_plate
        self._records = {}
        

"""
Main Data---------------------------------------------------------------
"""
class System:

    begin = datetime.date(2015, 8, 31)
    finish = datetime.date(2016, 11, 30)
    baseline = 19.4000
    final = 83.3333
    increment = (final - baseline) / abs(finish - begin).days
    
class Sheet:

    objects = {}
    
    version_1 = datetime.date(2015, 8, 31)
    version_2 = datetime.date(2015, 9, 8)

    def __init__(self, file):
        self._file = file
        self._version = '0'
        self._records = {}
        Sheet.objects[(self._file)] = self

    def read_sheet(self):
        reader = csv.reader(open(self._file, 'r', newline=''),
                            delimiter=',', quotechar='|')
        meta = False
        columns = False
        data = False
        direction = '1'
        meta_vars = []
        column_vars = []
        for row in reader:
            # <Handle Types>
            # Blank row handle
            if not row:
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
                self.check_metadata()
                continue
            # </Handle Types>
            #
            # Metadata
            if meta == True:
                try:
                    exec('self._' + str(row[0]).lower() + '=\'' + str(row[1]) +
                         '\'')
                except:
                    raise ValueError('Metadata error in ' + str(self._file))
            # Columns
            if columns == True:
                i = 3
                while i < len(row):
                    exec('self._' + str(row[0]).lower() + '_' + str(i) +'=\'' +
                         str(row[i]) + '\'')
                    i += 1
            # Data
            if data == True:
                if int(self._version) == 3:
                    self.process_version_3(row)
                elif int(self._version) == 2 or int(self._version) == 1:
                    direction = self.process_version_1_and_2(row, direction)
                """
                except:
                    raise ValueError('Version not recognized for ' +
                                     str(self._file))
                """
        return True

    def check_metadata(self):
        # Update! Make values dependent on version
        values = ['sheet', 'version', 'driver', 'year', 'month', 'day',
                  'vehicle', 'mileage_start', 'mileage_end', 'mileage_total']
        for value in values:
            try:
                eval('self._' + value)
            except:
                raise AttributeError(self._file + ' is missing ' + value)
        return True

    def process_version_3(self, row):
        if row[0] == 'Boarding':
            return False
        if row[2] == '0':
            return False
        if not re.sub(' ', '', ''.join(row)):
            return False
        # STOP VALIDATION HERE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1
        if not row[0]:
            raise ValueError(self._file + ' does not have a boarding')
        if not row[1]:
            raise ValueError(self._file + ' does not have a time')
        if not row[2]:
            raise ValueError(self._file + ' does not have a count')
        if not row[3]:
            raise ValueError(self._file + ' does not have a deboarding')
        record = Record(self._year, self._month, self._day, self._sheet,
                        row[0][0], self._driver, self._vehicle, row[1],
                        '', row[0], 'On', row[2])
        self._records[(row[1], 'On', row[1])] = record
        record = Record(self._year, self._month, self._day, self._sheet,
                        row[3][0], self._driver, self._vehicle, row[1],
                        '', row[3], 'Off', row[2])
        self._records[(row[3], 'Off', row[1])] = record
        return True

    def process_version_1_and_2(self, row, direction):
        if row[0] == 'Return':
            direction = '2'
            return direction
        entry = 'On'
        if row[2] == 'Off':
            entry = 'Off'
        i = 3
        while i < len(row):
            if re.sub(' ', '', row[i]):
                try:
                    # Set direction
                    if direction == '1':
                        direct = self._direction_1
                    else:
                        direct = self._direction_2
                    # Set time
                    if eval('self._version') == '2':
                        time = eval('self._depart_' + self._direction_1[-2:
                                    ].lower() + '_' + str(i))
                        if not time:
                            time = eval('self._depart_' + self._direction_2[-2:
                                        ].lower() + '_' + str(i))
                    elif eval('self._version') == '1':
                        time = eval('self._time_' + str(i))
                    else:
                        raise ValueError('Version ' + str(eval(
                            'self._version')) + 'does not exist')
                    record = Record(self._year, self._month, self._day,
                                    self._sheet, self._route, self._driver,
                                    self._vehicle, time, direct, row[1], entry,
                                    row[i])
                    self._records[(row[1], entry, time)] = record
                except:
                    raise ValueError('Columns do not match the number of ' +
                                     'data columns in: ' + str(self._file) +
                                     '; with the row that begins with: ' +
                                     str(', '.join(row[0:3])) + '; at  index: '
                                     + str(i))
            i += 1
        return direction

    def change_value(self, from_value, to_value):
        # This is used to typically change metadata feature values
        sheet_data = []
        # Read in rows
        reader = csv.reader(open(self._file, 'r', newline=''),
                            delimiter=',', quotechar='|')
        for row in reader:
            new_row = []
            for entry in row:
                # If entry equals value to change, change it by appending
                if entry == from_value:
                    new_row.append(to_value)
                # Otherwise add the value as it was
                else:
                    new_row.append(entry)
            sheet_data.append(new_row)
        # Write final rows
        writer = csv.writer(open(self._file, 'w', newline=''),
                            delimiter=',', quotechar='|')
        for row in sheet_data:
            writer.writerow(row)
        return True

    def change_metadata(self, from_feature, to_feature, prev, value='',
                        overwrite=False):
        sheet_data = []
        # Read in rows
        reader = csv.reader(open(self._file, 'r', newline=''),
                            delimiter=',', quotechar='|')
        i = 0
        index = {}
        features = {}
        for row in reader:
            index[i] = (row[0], row[1:])
            features[row[0]] = i
            i += 1
        match = False
        for feat in from_feature:
            if feat in features:
                if match == True:
                    print('More than one from feature discovered for ' +
                          str(to_feature) + ', only last value will be kept')
                match = True
                # If in wrong location change index
                if features[prev] != features[feat] - 1:
                    index[features[prev] + 0.5] = index[features[feat]]
                    del index[features[feat]]
                    features[feat] = features[prev] + 0.5
                # Set to_feature index as current from_feature index
                features[to_feature] = features[feat]
                # Revise index values to reflect to_feature name
                if not overwrite:
                    index[features[to_feature]] = (to_feature,
                                                   index[features[feat]][1])
                else:
                    index[features[to_feature]] = (to_feature, value)
                del features[feat]
        # If no matches found, add value
        try:
            if not match and to_feature not in features:
                index[(features[prev] + 0.5)] = (to_feature, value)
                features[to_feature] = (features[prev] + 0.5)
        except:
            print('Could not change metadata for ' + str(self._file))
        # Write final rows
        writer = csv.writer(open(self._file, 'w', newline=''),
                            delimiter=',', quotechar='|')
        for entry in sorted(index.keys()):
            if not isinstance(index[entry][1], list):
                writer.writerow([index[entry][0]] + [index[entry][1]])
            else:
                writer.writerow([index[entry][0]] + index[entry][1])
        return True

    def add_metadata(self, feature, value, prev):
        sheet_data = []
        # Read in rows
        reader = csv.reader(open(self._file, 'r', newline=''),
                            delimiter=',', quotechar='|')
        for row in reader:
            sheet_data.append(row)
            # If previous entry matches prev, add feature and value
            if row[0] == prev:
                sheet_data.append([feature, value])
        # Write final rows
        writer = csv.writer(open(self._file, 'w', newline=''),
                            delimiter=',', quotechar='|')
        for row in sheet_data:
            writer.writerow(row)
        return True

    def delete_metadata(self, feature):
        sheet_data = []
        # Read in rows
        reader = csv.reader(open(self._file, 'r', newline=''),
                            delimiter=',', quotechar='|')
        for row in reader:
            # If the row feature is not equal to the feature, add to data
            if row[0] != feature:
                sheet_data.append(row)
        # Write final rows
        writer = csv.writer(open(self._file, 'w', newline=''),
                            delimiter=',', quotechar='|')
        for row in sheet_data:
            writer.writerow(row)
        return True

    def add_data(self, feature, prev):
        sheet_data = []
        # Read in rows
        reader = csv.reader(open(self._file, 'r', newline=''),
                            delimiter=',', quotechar='|')
        for row in reader:
            sheet_data.append(row)
            # If previous entry matches prev, add feature and value
            if row[0:len(prev)] == prev:
                sheet_data.append(feature)
        # Write final rows
        writer = csv.writer(open(self._file, 'w', newline=''),
                            delimiter=',', quotechar='|')
        for row in sheet_data:
            writer.writerow(row)
        return True

    def delete_data(self, feature):
        sheet_data = []
        # Read in rows
        reader = csv.reader(open(self._file, 'r', newline=''),
                            delimiter=',', quotechar='|')
        for row in reader:
            # If the row feature is not equal to the feature, add to data
            if row != feature:
                sheet_data.append(row)
        # Write final rows
        writer = csv.writer(open(self._file, 'w', newline=''),
                            delimiter=',', quotechar='|')
        for row in sheet_data:
            writer.writerow(row)
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
            print(year, month, day, sheet, stop)
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
        if not os.path.exists('Reports/Weekly'):
            os.mkdir('Reports/Weekly')
        if not os.path.exists('Reports/Weekly/CSV'):
            os.mkdir('Reports/Weekly/CSV')
        for week in sorted(Week.objects.keys()):
            # Open workbook and worksheet
            workbook = xlsxwriter.Workbook('Reports/Weekly/CSV/' + str(week) +
                                           '.xlsx')
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
        if not os.path.exists('Reports/Monthly'):
            os.mkdir('Reports/Monthly')
        if not os.path.exists('Reports/Monthly/CSV'):
            os.mkdir('Reports/Monthly/CSV')
        for month in sorted(Month.objects.keys()):
            writer = csv.writer(
                open('Reports/Monthly/CSV/' + str(month) + '.csv', 'w',
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
        if not os.path.isdir('reports'):
            os.makedirs('reports')
        writer = csv.writer(open('reports/Ridership_' + '_'.join(features
                                 ).title() + '.csv', 'w', newline=''),
                            delimiter=',', quotechar='|')
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
def sheet_cleanup(regex):
    for dirpath, dirnames, filenames in os.walk("."):
        for filename in [f for f in filenames if re.search(regex, f)]:
            reader = csv.reader(open((str(dirpath) + '/' + str(filename))[2:],
                                     'r', newline=''),
                                delimiter=',', quotechar='|')
            writer = csv.writer(open(dirpath + '/' + filename[5:7] +
                filename[0:4] + '_S' + filename[8] + '.csv', 'w', newline=''),
                                delimiter=',', quotechar='|')
            for row in reader:
                writer.writerow(row)
    return True

#sheet_cleanup('^\d{7}S\d.csv$')
#print('Finished cleaning sheets')
    
for dirpath, dirnames, filenames in os.walk("."):
    for filename in [f for f in filenames if re.search('\d{6}_S\d',
                                                       f)]:
        obj = Sheet((str(dirpath) + '/' + str(filename)))
        #obj = Sheet((str(dirpath) + '/' + str(filename))[2:])
        obj.change_metadata(['Car wash', 'car wash', 'Car_wash'],
                            'Car_Wash', 'Fuel_Cost', value=0, overwrite=False)
        obj.read_sheet()


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
