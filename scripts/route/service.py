#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

# Python libraries and packages
import datetime
import re

# Import scripts from src
from src.scripts.route.errors import *
from src.scripts.utils.classes import DataModelTemplate

# Import variables from src
from src.scripts.constants import *


class Service(DataModelTemplate):

    json_path = '{}/route/service.json'.format(DATA_PATH)
    objects = {}

    def set_object_attrs(self):
        self.start_date = datetime.datetime.strptime(self.start_date, '%Y-%m-%d')
        self.end_date = datetime.datetime.strptime(self.end_date, '%Y-%m-%d')
        self.segments = {}

    def __repr__(self):
        return '<Service {}>'.format(self.id)

    def __lt__(self, other):
        return self.id < other.id

    def __le__(self, other):
        return self.id <= other.id

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        return self.id != other.id

    def __gt__(self, other):
        return self.id > other.id

    def __ge__(self, other):
        return self.id >= other.id

    def __hash__(self):
        return hash(self.id)

    def get_json(self):
        attrs = dict([(k, getattr(self, k)) for k in ['id', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday',
                                                      'saturday', 'sunday', 'text']])
        attrs['start_date'] = self.start_date.strftime('%Y-%m-%d')
        attrs['end_date'] = self.end_date.strftime('%Y-%m-%d')
        return attrs

    def add_segment(self, segment):
        if segment not in self.segments:
            self.segments[segment] = True
        else:
            raise DuplicateServiceSheetError('Duplicate segment {} found in service {}'.format(segment, self.id))


class Holiday(DataModelTemplate):

    json_path = '{}/route/holiday.json'.format(DATA_PATH)
    objects = {}

    @classmethod
    def get_holidays(cls, past_filter=True):
        holidays = []
        for holiday in cls.objects:
            holiday = cls.objects[holiday]
            if past_filter and datetime.datetime.strptime(holiday.holiday, '%Y-%m-%d') < datetime.datetime.today():
                continue
            for obj in Service.objects:
                service = Service.objects[obj]
                # Check if the holiday applies to the given service dates
                if service.start_date <= datetime.datetime.strptime(holiday.holiday, '%Y-%m-%d') <= service.end_date:
                    holidays.append([service.id, re.sub('-', '', holiday.holiday), 2])
        return holidays