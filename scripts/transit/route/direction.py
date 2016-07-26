#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

# Import classes and functions from src
from src.scripts.utils.IOutils import load_json, export_json

# Import variables from src
from src.scripts.transit.constants import PATH


class Direction(object):

    objects = {}
    header_0 = 'direction_id'

    def __init__(self, id, name, description, origin, destination):
        self.id = int(id)
        self.name = name
        self.description = description
        self.origin = origin
        self.destination = destination
        Direction.objects[int(id)] = self

    def __repr__(self):
        return '<Direction {}>'.format(self.id)

    @classmethod
    def load(cls):
        load_json('{}/data/direction.json'.format(PATH), cls)

    @classmethod
    def export(cls):
        export_json('{}/data/direction.json'.format(PATH), cls)

