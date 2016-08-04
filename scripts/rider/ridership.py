#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

# Python libraries and packages
import datetime
import time
import xlsxwriter
import multiprocessing as mp

# Entire scripts from src
from src.scripts.route.route import load

# Classes and variables from src
from src.scripts.constants import *
from src.scripts.rider.constants import BEGIN, BASELINE, INCREMENT
from src.scripts.utils.classes import DataModelTemplate
from src.scripts.utils.IOutils import *


__author__ = 'Michael Lockwood'
__github__ = 'mlockwood'
__projectclass__ = 'go'
__projectsubclass__ = 'src/scripts/transit'
__project__ = 'rider'
__script__ = 'ridership.py'
__date__ = 'February2015'
__credits__ = None
__collaborators__ = None


load()


class Metadata(DataModelTemplate):

    json_path = '{}/metadata.json'.format(DATA_PATH)
    objects = {}

    def set_objects(self):
        Metadata.objects[self.sheet] = self


class Entry(DataModelTemplate):

    json_path = '{}/entry.json'.format(DATA_PATH)
    objects = {}

    def set_object_attrs(self):
        Period.add_count(datetime.datetime(*[int(i) for i in [self.metadata[:4], self.metadata[4:6],
                                                              self.metadata[6:8]]]),
                         self.count)

    def set_objects(self):
        Entry.objects[(self.metadata, self.time, self.on, self.off)] = self
    

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
    Metadata.load()
    Entry.load()
    print('Loading complete', time.clock() - start)
    Period.set_averages()
    print('Averages set', time.clock() - start)
    Period.publish()
    print('Publishing complete', time.clock() - start)
