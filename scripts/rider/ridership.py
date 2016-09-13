#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

import datetime
from dateutil import parser, tz
import xlsxwriter
import multiprocessing as mp

from src.scripts.constants import *
from src.scripts.rider.constants import BEGIN, BASELINE, INCREMENT, OUT_PATH
from src.scripts.utils.classes import DataModelTemplate
from src.scripts.utils.IOutils import *


__author__ = 'Michael Lockwood'
__github__ = 'mlockwood'


class Metadata(DataModelTemplate):

    json_path = '{}/rider/metadata.json'.format(DATA_PATH)
    objects = {}

    def set_object_attrs(self):
        self.login = parser.parse(self.login).astimezone(tz.gettz('America/Los_Angeles'))


class GetMetadata(DataModelTemplate):

    json_path = '{}/rider/get_metadata.json'.format(DATA_PATH)
    objects = {}

    def set_object_attrs(self):
        self.login = parser.parse(self.login).astimezone(tz.gettz('America/Los_Angeles'))


class Entry(DataModelTemplate):

    json_path = '{}/rider/entry.json'.format(DATA_PATH)
    objects = {}

    def set_object_attrs(self):
        meta = Metadata.objects[self.metadata]
        Record.add_entry([meta.login.year, meta.login.month, meta.login.day, meta.driver, meta.schedule, self.time,
                          self.on, self.off, self.count])
        Period.add_count(meta.login, self.count)


class GetEntry(DataModelTemplate):

    json_path = '{}/rider/get_entry.json'.format(DATA_PATH)
    objects = {}

    def set_object_attrs(self):
        meta = GetMetadata.objects[self.metadata]
        Record.add_entry([meta.login.year, meta.login.month, meta.login.day, meta.driver, meta.schedule, self.time,
                          self.on, self.off, self.count])
        Period.add_count(meta.login, self.count)


class Record(object):

    data = []
    stops = {}
    locs = {}

    @staticmethod
    def add_entry(entry):
        Record.data.append(entry)

    @staticmethod
    def publish():
        set_directory(OUT_PATH)
        writer = open('{}/records.csv'.format(OUT_PATH), 'w')
        for entry in Record.data:
            writer.write('{}\n'.format(','.join(str(s) for s in entry)))
        writer.close()


class Period(object):

    objects = {}
    periods = {}

    def __init__(self, date):
        self.date = date
        self.count = 0
        self.average = 0
        self.straight_line = INCREMENT * abs(date - BEGIN).days + BASELINE
        self.set_key('{0}_{1:2d}'.format(self.date.isocalendar()[0], self.date.isocalendar()[1]), 'weekly')
        self.set_key('{}_{}'.format(str(self.date.year), str(self.date.month)), 'monthly')
        self.set_key(self.date.year, 'annual')
        self.set_key('total', 'total')
        Period.objects[date] = self

    def set_key(self, key, period):
        if (key, period) not in Period.periods:
            Period.periods[(key, period)] = {}
        Period.periods[(key, period)][self.date] = self

    @staticmethod
    def add_count(date, count):
        date = date.replace(hour=0, minute=0, second=0)
        if date not in Period.objects:
            Period(date)
        Period.objects[date].count += count

    @staticmethod
    def set_averages():
        for date in sorted(Period.objects.keys()):
            prev = Period.seek_prev_dow(date)
            average, total, count = prev.average if prev else (0, 0, 0)
            new_total, new_count = ((total + Period.objects[date].count), (count + 1))
            Period.objects[date].average = (new_total / new_count, new_total, new_count)

    @staticmethod
    def seek_prev_dow(date):
        if date < datetime.datetime(2015, 8, 31, tzinfo=tz.gettz('America/Los_Angeles')):
            return None
        elif date - datetime.timedelta(days=7) in Period.objects:
            return Period.objects[date - datetime.timedelta(days=7)]
        else:
            return Period.seek_prev_dow(date - datetime.timedelta(days=7))

    @staticmethod
    def publish():
        outputs = []
        for key in Period.periods:
            set_directory('{}/{}'.format(OUT_PATH, key[1]))
            filename = '{}/{}/{}.xlsx'.format(OUT_PATH, key[1], key[0])
            outputs.append((Period.periods[key], filename))

        p = mp.Pool()
        p.map(Period.write_file, outputs)

    @staticmethod
    def add_series(chart, name, row, column, color):
        chart.add_series({'name': name, 'line': {'color': color},
                          'categories': '=Ridership!$B$2:$B${}'.format(str(row - 1)),
                          'values': '=Ridership!${0}$2:${0}${1}'.format(column, str(row - 1)),
                          })

    @staticmethod
    def write_file(args):
        obj = args[0]

        # Open workbook and worksheet
        workbook = xlsxwriter.Workbook(args[1])
        worksheet = workbook.add_worksheet('Ridership')
        chart = workbook.add_chart({'type': 'line'})

        # Set column widths
        [worksheet.set_column('{0}:{0}'.format(str(chr(x))), 12) for x in range(65, 70)]

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
        Period.add_series(chart, 'Ridership', row, 'C', '#008000')
        Period.add_series(chart, 'Average', row, 'D', '#000080')
        Period.add_series(chart, 'Pilot', row, 'E', '#808080')

        # Set chart ancillary information
        chart.set_title({'name': 'GO Transit Ridership'})
        chart.set_x_axis({'name': 'Day'})
        chart.set_y_axis({'name': 'Riders'})

        # Insert chart into the worksheet
        worksheet.insert_chart('A' + str(row + 2), chart, {'x_offset': 10, 'y_offset': 10})
        workbook.close()


if __name__ == "__main__":
    Metadata.load()
    Entry.load()
    GetMetadata.load()
    GetEntry.load()
    Record.publish()
    Period.set_averages()
    Period.publish()
