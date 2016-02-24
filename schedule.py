
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
        stop = st.Stop.obj_map[record._stop]._name
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
    def publish():
        if not os.path.exists(System.path +
                              '/reports/schedules/timetables'):
            os.makedirs(System.path +
                        '/reports/schedules/timetables')
        # Iterate through each stop
        for stop in sorted(Stop.objects.keys()):
            if not stop:
                continue
            # Set object
            obj = Stop.objects[stop]
            # Build a timetable for each sign at the stop (by gps_ref)
            for ref in sorted(obj._records.keys()):
                # Add html document information
                doc = ('<!doctype html>\n' +
                       '<!--[if lt IE 7]> ' +
                       '<html class="lt-ie9 lt-ie8 lt-ie7" lang="en">' +
                       '<![endif]-->\n' +
                       '<!--[if IE 7]>' +
                       '<html class="lt-ie9 lt-ie8" lang="en">' +
                       '<![endif]-->\n' +
                       '<!--[if IE 8]>' +
                       '<html class="lt-ie9" lang="en">' +
                       '<![endif]-->\n' +
                       '<!--[if gt IE 8]><!-->' +
                       '<html lang="en">' +
                       '<!--<![endif]-->\n' +
                       '<head>\n' +
                       '\t<title>GO TRANSIT TIMETABLE</title>\n' +
                       '\t<link rel="stylesheet" href="css/timetable.css">\n' +
                       '</head>\n' +
                       '<body>\n' +
                       '\t<div id="stop">' + stop +
                       '</div>\n' +
                       '\t<div class="main">\n')
                # Review each route at the stop ref
                for route in sorted(obj._records[ref]):
                    # Find stop direction for stop, ref, route
                    stop_id = str(eval('st.Stop.obj_map[stop]._route' +
                                       route[0]))
                    direction = st.Point.objects[(stop_id, ref)]._direction
                    if direction == 'Pendleton Shoppette':
                        direction = 'Pend. Shoppette'
                    elif direction == 'Joint Base Headquarters':
                        direction = 'Joint Base HQ'
                    # Find service days
                    weekdays = rt.Route.objects[route]._weekdays
                    if weekdays == [1, 2, 3, 4, 5]:
                        days = 'MONDAY - FRIDAY'
                    elif weekdays == [6, 7]:
                        days = 'SATURDAY & SUNDAY'
                    else:
                        raise ValueError('Weekdays for Route ' + route +
                            ' are unknown. Please define in schedule.py.')
                    # Add basic route information and headers
                    doc += ('\t\t<div class="route">\n' +
                            '\t\t\t<img src="img/route' + route +
                            '_logo.jpg" class="imgHeader" />\n' +
                            '\t\t\t<div class="dirHeader" id="rt' + route +
                            '">TO ' + direction.upper() + '</div>\n' +
                            '\t\t\t<div class="table">\n' +
                            '\t\t\t\t<div class="dayHeader">' + days +
                            '</div>\n' +
                            '\t\t\t\t<div class="column">\n')
                    # Add time entries
                    i = 0
                    times = sorted(obj._records[ref][route])
                    while i < 40:
                        # Cap columns at twenty entries
                        if i == 20:
                            doc += ('\t\t\t\t</div>\n' +
                                    '\t\t\t\t<div class="column">\n')
                        if i < len(times):
                            # If the entry is 12:00 or later, make it bold
                            if int(times[i][0:2]) >= 12:
                                doc += ('\t\t\t\t\t<div class="entry bold">' +
                                        times[i] + '</div>\n')
                            # Otherwise do not bold it
                            else:
                                doc += ('\t\t\t\t\t<div class="entry">' +
                                        times[i] + '</div>\n')
                        # Handle empty entries
                        else:
                            doc += '\t\t\t\t\t<div class="entry"></div>\n'
                        i += 1
                    # Close route divs
                    doc += '\t\t\t\t</div>\n\t\t\t</div>\n\t\t</div>\n'
                # Add footer
                doc += ('\t<div id="footer">\n' +
                        '\t\t<div id="footerText">\n' +
                        '\t\t\t<p>For questions or assistance planning your ' +
                        'trip, please call the Transit Supervisor at (253) ' +
                        '966-3939.</p>\n' +
                        '\t\t\t<p>All times are estimated for public ' +
                        'guidance only. GO Transit does not operate on ' +
                        'Federal Holidays.</p>\n' +
                        '\t\t\t<p>For current route maps and schedules ' +
                        'please visit www.facebook.com/GoLewisMcChord.</p>\n' +
                        '\t\t</div>\n' +
                        '\t\t<img src="img/go_logo.jpg" id="footerImg" />\n' +
                        '\t</div>\n' +
                        '</body>\n' +
                        '</html>\n')
                # Write document
                writer = open(System.path + '/reports/schedules/timetables/' +
                              re.sub(' |\-', '_', stop) + '_' + str(ref) +
                              '.html', 'w')
                writer.write(doc)
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
