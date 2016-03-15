
import configparser
import csv
import datetime
import os
import re
import sys
import xlsxwriter

from jinja2 import Template

"""
GO Imports-------------------------------------------------------------
"""
import src.scripts.transit.constants as System
import src.scripts.transit.route.route as rt
import src.scripts.transit.stop.stop as st

"""
Main Classes------------------------------------------------------------
"""

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


def publish():
    if not os.path.exists(System.path + '/reports/schedules/routes'):
        os.makedirs(System.path + '/reports/schedules/routes')
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

class Schedule:

    objects = {}

    def __init__(self, route, schedule, entries):
        self._route = route
        self._schedule = schedule
        self._entries = entries
        Schedule.objects[(route, schedule)] = self


"""
User Interface----------------------------------------------------------
"""
process()
publish()
