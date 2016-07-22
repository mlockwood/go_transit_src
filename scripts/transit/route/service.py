#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

# Python libraries and packages
import datetime

# Import scripts from src
from src.scripts.transit.route.errors import *
from src.scripts.utils.classes import DataModelTemplate

# Import variables from src
from src.scripts.transit.constants import PATH


class Service(DataModelTemplate):

    json_path = '{}/data/service.json'.format(PATH)
    objects = {}

    def set_object_attrs(self):
        self.start_date = datetime.datetime.strptime(self.start_date, '%Y%m%d')
        self.end_date = datetime.datetime.strptime(self.end_date, '%Y%m%d')
        self.segments = {}

    def __repr__(self):
        return '<Direction {}>'.format(id)

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
