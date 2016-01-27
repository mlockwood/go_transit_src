
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

class Sheet:

    objects = {}
    header = ['Stop', 'Spread1', 'Spread2', 'GPS', 'Display']

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
        for dirpath, dirnames, filenames in os.walk(System.go_transit_path
                                                    + '/data/schedules/'):
            for filename in [f for f in filenames if re.search(
                'schedule_\d{6}', f)]:
                obj = Sheet((str(dirpath) + '/' + str(filename)))
                obj.read_sheet()
        return True

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
        # Processing functions
        self.set_id()
        self.append_record()
        # Add records
        Stop.add_record(self)
        Route.add_record(self)

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

class Stop:

    objects = {}

    def __init__(self, stop, display):
        self._stop = stop
        self._display = display
        self._records = {}
        Stop.objects[stop] = self

    @staticmethod
    def add_record(record):
        # Set and handle stop object
        if record._stop not in Stop.objects:
            Stop(record._stop, record._display)
        obj = Stop.objects[record._stop]
        # Add stop, direction, time
        if record._gps_ref not in obj._records:
            obj._records[record._gps_ref] = {}
        if record._route not in obj._records[record._gps_ref]:
            obj._records[record._gps_ref][record._route] = []
        obj._records[record._gps_ref][record._route].append(record._time)
        return True

    @staticmethod
    def _stack_times(a, n):
        i = 0
        b = []
        c = []
        for entry in a:
            if i < n:
                c.append(entry)
                i += 1
            elif i == n:
                b.append(c)
                c = [entry]
                i = 1
        while i < n:
            c.append('')
            i += 1
        b.append(c)
        return [list(x) for x in zip(*b)]

    @staticmethod
    def prepare_table(D):
        cells = {}
        temp = []
        for route in D:
            temp.append(Stop._stack_times(D[route], 15))
            cells[route] = len(temp[-1][0])
        i = 0
        stop_matrix = []
        while i < len(temp[0]):
            cur = []
            for route in temp:
                cur += route[i]
            stop_matrix.append(cur)
            i += 1
        return stop_matrix, cells

    @staticmethod
    def publish():
        if not os.path.exists(System.go_transit_path +
                              '/reports/schedules/timetables'):
            os.makedirs(System.go_transit_path +
                        '/reports/schedules/timetables')
        # Iterate through each stop
        for stop in sorted(Stop.objects.keys()):
            # Set object
            obj = Stop.objects[stop]
            # Build a timetable for each sign at the stop (by gps_ref)
            for ref in sorted(obj._records.keys()):
                # Create stop_matrix table with cell widths for the headers
                stop_matrix, cells = Stop.prepare_table(obj._records[ref])
                summation = 0
                for cell in cells:
                    summation += cells[cell]
                # Open workbook and worksheet
                workbook = xlsxwriter.Workbook(System.go_transit_path +
                    '/reports/schedules/timetables/' + str(stop) + '_' +
                    re.sub(' |\-', '_', str(st.Stop.obj_map[stop]._name)
                    ).title() + '_' + str(ref) + '.xlsx')
                worksheet = workbook.add_worksheet('Timetable')
                
                # Set column widths
                alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
                            'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T']
                i = 0
                while i < summation:
                    worksheet.set_column(eval('\'' + alphabet[i] + ':' +
                                         alphabet[i] + '\''), 12)
                    i += 1
                
                # Format declarations
                merge_format = workbook.add_format({'bold': True,
                                                    'align': 'center',
                                                    'fg_color': '#D7E4BC',
                                                    })
                bold_format = workbook.add_format({'bold': True,
                                                   'align': 'center',
                                                   })
                center_format = workbook.add_format({'align': 'center',
                                                     'valign': 'vcenter',
                                                     })
                
                # Write header
                worksheet.merge_range(eval('\'A1:' + alphabet[summation - 1] +
                    '1\''), 'Stop ' + str(stop), merge_format)
                # Write subheaders for each route
                i = 0
                for cell in sorted(cells.keys()):
                    worksheet.merge_range(eval('\'' + alphabet[i] + '2:' +
                        alphabet[i + cells[cell] - 1] + '2\''), 'Route ' +
                        str(cell), bold_format)
                    i += cells[cell]
                
                # Write data
                row = 3
                for line in stop_matrix:
                    worksheet.write_row('A' + str(row), line , center_format)
                    row += 1
                    
                # Close workbook
                workbook.close()
        return True

class Route:

    objects = {}

    def __init__(self, route, dir1, dir2):
        self._route = route
        self._dir1 = dir1
        self._dir2 = dir2
        self._records = {}
        Route.objects[route] = self

    @staticmethod
    def add_record(record):
        # Set and handle route object
        if record._route not in Route.objects:
            Route(record._route,
                  record._sheet._direction1,
                  record._sheet._direction2)
        obj = Route.objects[record._route]
        # Add stop, direction, time
        if record._stop not in obj._records:
            obj._records[record._stop] = {}
        if record._direction not in obj._records[record._stop]:
            obj._records[record._stop][record._direction] = []
        obj._records[record._stop][record._direction].append(record._time)
        return True

    @staticmethod
    def publish():
        if not os.path.exists(System.go_transit_path +
                              '/reports/schedules/routes'):
            os.makedirs(System.go_transit_path +
                        '/reports/schedules/routes')
        for route in sorted(Route.objects.keys()):
            # Set object
            obj = Route.objects[route]
            # Open workbook and worksheet
            workbook = xlsxwriter.Workbook(System.go_transit_path +
                '/reports/schedules/routes/route' + str(route) + '.xlsx')
            worksheet = workbook.add_worksheet('Schedule')
            # Set column widths
            worksheet.set_column('A:A', 20)
            worksheet.set_column('B:B', 36)
            worksheet.set_column('C:C', 36)
            
            # Format declarations
            merge_format = workbook.add_format({'bold': True,
                                                'align': 'center',
                                                'fg_color': '#D7E4BC',
                                                })
            bold_format = workbook.add_format({'bold': True,
                                               'align': 'center',
                                               })
            center_format = workbook.add_format({'align': 'center',
                                                 'valign': 'vcenter',
                                                 })
            stop_format = workbook.add_format({'bold': True,
                                               'align': 'center',
                                               'valign': 'vcenter',
                                               'text_wrap': True,
                                               })
            text_wrap_format = workbook.add_format({'text_wrap': True})
            
            # Write header
            worksheet.merge_range('A1:C1', 'Route ' + str(route), merge_format)
            worksheet.write_row('A2', ['Stop', 'To ' + obj._dir1.title(),
                'To ' + obj._dir2.title()], bold_format)
            
            # Write data
            row = 3
            for stop in sorted(obj._records.keys()):
                #if Stop.objects[stop]._display == '0':
                #    continue
                worksheet.write('A' + str(row), str(st.Stop.obj_map[str(stop
                    ).lower()]._name).title(), stop_format)
                # Add first direction times
                try:
                    worksheet.write('B' + str(row), ', '.join(sorted(
                        obj._records[stop][obj._dir1])), text_wrap_format)
                except:
                    worksheet.write('B' + str(row), '--', center_format)
                # Add second direction times
                try:
                    worksheet.write('C' + str(row), ', '.join(sorted(
                        obj._records[stop][obj._dir2])), text_wrap_format)
                except:
                    worksheet.write('C' + str(row), '--', center_format)
                row += 1
                
            # Close workbook
            workbook.close()
        return True

def publish():
    # Records
    Record.publish_matrix()
    # Stop
    Stop.publish()
    # Route
    Route.publish()

"""
User Interface----------------------------------------------------------
"""
Sheet.process()
publish()

start = datetime.date(2015, 11, 1)
end = datetime.date(2016, 12, 31)

rp.Report.path = System.go_transit_path + '/reports/schedules/'
rp.Report.name = 'Schedule_'

rp_obj = rp.Report(rp.convert_objects(Record.objects))


rp_obj.generate(['route', 'stop', 'time', 'direction'], start=start, end=end)
