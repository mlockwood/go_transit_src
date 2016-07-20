#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

# Python libraries and packages
import datetime

# Import scripts from src
from src.scripts.transit.route.errors import *
from src.scripts.utils.IOutils import load_json, export_json

# Import variables from src
from src.scripts.transit.constants import PATH


class Service(object):

    objects = {}

    def __init__(self, id, monday, tuesday, wednesday, thursday, friday, saturday, sunday, start_date, end_date, text):
        self.id = int(id)
        self.monday = monday
        self.tuesday = tuesday
        self.wednesday = wednesday
        self.thursday = thursday
        self.friday = friday
        self.saturday = saturday
        self.sunday = sunday
        self.start_date = datetime.datetime.strptime(start_date, '%Y%m%d')
        self.end_date = datetime.datetime.strptime(end_date, '%Y%m%d')

        self.text = text
        self.segments = {}

        Service.objects[int(id)] = self

    def __repr__(self):
        return '<Direction {}>'.format(id)

    @classmethod
    def load(cls):
        load_json('{}/data/routes/service.json'.format(PATH), cls)

    @classmethod
    def export(cls):
        export_json('{}/data/routes/service.json'.format(PATH), cls)

    def get_json(self):
        attrs = dict([(k, getattr(self, k)) for k in ['id', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday',
                                                      'saturday', 'sunday', 'text']])
        attrs['start_date'] = self.start_date.strftime('%Y%m%d')
        attrs['end_date'] = self.end_date.strftime('%Y%m%d')
        return attrs

    def add_segment(self, segment):
        if segment not in self.segments:
            self.segments[segment] = True
        else:
            raise DuplicateServiceSheetError('Duplicate segment {} found in service {}'.format(segment, self.id))
