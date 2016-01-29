
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
import report as rp

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

class Route:

    objects = {}

    def __init__(self, data, sheet):
        self._records = sheet._records
        for attr in data:
            try:
                exec('self.' + attr[0] + '=' + attr[1])
                if isinstance(eval('self._' + attr[0], complex)):
                    exec('self.' + attr[0] + '=\'' + attr[1] + '\'')
            except:
                try:
                    exec('self.' + attr[0] + '=\'' + attr[1] + '\'')
                except:
                    self._date = attr[1]
        Route.objects[self._route] = self

class Sheet:

    objects = {}
    header = ['Stop', 'Spread1', 'Spread2', 'Points', 'Display']

    def __init__(self, file):
        self._file = file
        self._start_shift = ''
        self._time_key = 0
        self._records = {}
        self._entries = []
        self._temp = {}
        Sheet.objects[self._file] = self

    @staticmethod
    def process():
        Sheet.load_config()
        for dirpath, dirnames, filenames in os.walk(System.go_transit_path
                                                    + '/data/schedules/'):
            for filename in [f for f in filenames if re.search(
                'schedule_\d{6}', f)]:
                obj = Sheet((str(dirpath) + '/' + str(filename)))
                obj.read_sheet()
        Sheet.sheet_to_route()
        return True

    @staticmethod
    def load_config():
        config = configparser.ConfigParser()
        config.read('route.ini')
        if config['USER']['toggle'] == 'False':
            Sheet.date = datetime.date.today()
        else:
            Sheet.date = datetime.date(int(config['USER']['year']),
                                       int(config['USER']['month']),
                                       int(config['USER']['day']))
        return True

    @staticmethod
    def sheet_to_route():
        # Set all sheets in routes DS by {route: {date: sheet_obj}}
        routes = {}
        for sheet in Sheet.objects:
            obj = Sheet.objects[sheet]
            if obj._route not in routes:
                routes[obj._route] = {}
            routes[obj._route][obj._date] = obj

        # Select the routes which have a date matching Sheet.date
        for route in routes:
            for date in sorted(routes[route].keys(), reverse=True):
                # If the current option is less than or equal to the date,
                # select this option for the route
                if date <= Sheet.date:
                    data = []
                    for attr in dir(routes[route][date]):
                        if attr[0:2] != '__' and attr != '_results':
                            data.append((attr, eval('routes[route][date].' +
                                                    attr)))
                    Route(data, routes[route][date])
                    continue
                    

    def read_sheet(self):
        reader = csv.reader(open(self._file, 'r', newline=''),
                            delimiter=',', quotechar='|')
        meta = False
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
                meta = False
                continue
            # </Handle Types>
            
            # Metadata
            if meta == True:
                # Handle metadata category
                cur_meta = re.sub(' ', '', str(row[0]).lower())
                # Handle metadata value
                cur_value = str(row[1]).lower()
                # Add metadata to the sheet
                if re.search('\[', cur_value):
                    cur_value = re.sub('&', ',', cur_value)
                    exec('self._' + cur_meta + '=' + cur_value)
                else:
                    try:
                        exec('self._' + cur_meta + '=\'' + cur_value + '\'')
                    except:
                        raise ValueError('Metadata error in ' + cur_meta)
                        
            # Data
            if data == True:
                if row != Sheet.header:
                    self._entries.append(row)

        # If no data, alert user just in case of error
        if data == False:
            print(self._file, 'does not contain any data.')
        # Actually process records
        self._date = datetime.date(int(self._year), int(self._month),
                                   int(self._day))
        self.set_records()
        return True

    def set_records(self):
        # Set daily start and end times
        start = datetime.datetime(int(self._year), int(self._month),
                                  int(self._day), int(self._start[:-2]),
                                  int(self._start[-2:]))
        end = datetime.datetime(int(self._year), int(self._month),
                                int(self._day), int(self._end[:-2]),
                                int(self._end[-2:]))

        # Handle processing for each entry
        for entry in self._entries:
            # General record validation
            if entry == Sheet.header:
                continue
            if not re.sub(' ', '', ''.join(str(x) for x in entry)):
                continue
            
            # Stop validation and mapping=
            if str(entry[0]).lower() in st.Stop.obj_map:
                on = str(st.Stop.obj_map[str(entry[0]).lower()]._stop_id)
            else:
                raise ValueError('Stop ' + str(entry[0]) + ' from file ' +
                                 str(self._file) + ' is not recognized.')

            # GPS reference handling
            gps_ref = re.split('&', entry[3])

            # Process entries
            self.process_entry(entry[0], entry[1], gps_ref[0],
                               self._direction1, entry[4], start, end, '1')
            self.process_entry(entry[0], entry[2], gps_ref[1],
                               self._direction2, entry[4], start, end, '2')
        return True

    def process_entry(self, stop, spread, gps_ref, direction, display, base,
                      end, seq):
        if spread == 'n' or spread == 'd':
            return False
        # Base time is start + spread + offset
        base = base + datetime.timedelta(0, 60 * (int(spread) +
            eval('int(self._offset' + seq + ')')))
        # If spread + offset >= headway then reduce base by headway time
        if (int(spread) + eval('int(self._offset' + seq + ')') >=
            int(self._headway)):
            base = base - datetime.timedelta(0, 60 * int(self._headway))
        # Add records until end time
        while True:
            if base < end:
                Record(self._route, stop, gps_ref, direction,
                       base.strftime('%H:%M'), display, self._date, self)
            else:
                break
            base = base + datetime.timedelta(0, 60 * int(self._headway))
        return True
                            
class Record:

    objects = {}
    ID_generator = 1
    matrix_header = ['Route', 'Direction', 'Stop', 'Time', 'Display']
    matrix = [matrix_header]

    def __init__(self, route, stop, gps_ref, direction, time, display, date,
                 sheet):
        # Default values
        self._route = route
        self._stop = stop
        self._gps_ref = gps_ref
        self._direction = direction
        self._time = time
        self._display = display
        self._date = date
        self._count = 1
        self._sheet = sheet
        sheet._records[self] = True
        # Processing functions
        self.set_id()
        self.append_record()

    def set_id(self):
        self._ID = hex(Record.ID_generator)
        Record.ID_generator += 1
        Record.objects[self._ID] = self
        return True

    def append_record(self):
        Record.matrix.append([self._route, self._direction, self._stop,
                              self._time, self._display])
        return True

    @staticmethod
    def publish_matrix():
        if not os.path.exists(System.go_transit_path + '/reports/schedules'):
            os.makedirs(System.go_transit_path + '/reports/schedules')
        writer = csv.writer(open(System.go_transit_path +
            '/reports/schedules/records' +
            '.csv', 'w', newline=''), delimiter=',', quotechar='|')
        for row in Record.matrix:
            writer.writerow(row)
        return True


Sheet.process()
if __name__ == '__main__':
    Record.publish_matrix()
