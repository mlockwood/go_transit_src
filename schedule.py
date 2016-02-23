
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
import route as rt
import stop as st

"""
Main Classes------------------------------------------------------------
"""
class System:
    
    @staticmethod
    def load_config():
        config = configparser.ConfigParser()
        config.read('system.ini')
        for var in config['DEFAULT']:
            try:
                exec('System.' + var + ' = ' + eval('\'' +
                    eval('config[\'DEFAULT\'][\'' + var + '\']') + '\''))
                if isinstance('System.' + var, complex):
                    exec('System.' + var + ' = \'' + eval(
                        'config[\'DEFAULT\'][\'' + var + '\']') + '\'')
            except:
                exec('System.' + var + ' = \'' + eval(
                    'config[\'DEFAULT\'][\'' + var + '\']') + '\'')
        return True

System.load_config()

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
        stop = re.sub(' |\-', '_', str(st.Stop.obj_map[record._stop]._name)
                      ).title()
        if stop not in Stop.objects:
            Stop(stop, record._display)
        obj = Stop.objects[stop]
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
        for entry in sorted(a):
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
        for route in sorted(D.keys()):
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
        if not os.path.exists(System.path +
                              '/reports/schedules/timetables'):
            os.makedirs(System.path +
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
                workbook = xlsxwriter.Workbook(System.path +
                    '/reports/schedules/timetables/' + str(stop) + '_' +
                    str(ref) + '.xlsx')
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
                                                    'font_size': 18,
                                                    })
                bold_format = workbook.add_format({'bold': True,
                                                   'align': 'center',
                                                   })
                center_format = workbook.add_format({'align': 'center',
                                                     'valign': 'vcenter',
                                                     })
                
                # Write header
                worksheet.merge_range(eval('\'A1:' + alphabet[summation - 1] +
                    '1\''), re.sub('_', ' ', str(stop)), merge_format)
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
        if not os.path.exists(System.path +
                              '/reports/schedules/routes'):
            os.makedirs(System.path +
                        '/reports/schedules/routes')
        for route in sorted(Route.objects.keys()):
            # Set object
            obj = Route.objects[route]
            # Open workbook and worksheet
            workbook = xlsxwriter.Workbook(System.path +
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

def process():
    # Load routes from route.py
    for route in rt.Route.objects:
        for record in rt.Route.objects[route]._records:
            Stop.add_record(record)
            Route.add_record(record)
    return True

def publish():
    # Stop
    Stop.publish()
    # Route
    Route.publish()
    return True

"""
User Interface----------------------------------------------------------
"""
process()
publish()
