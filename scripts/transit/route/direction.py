#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

# Import classes and functions from src
from src.scripts.utils.classes import DataModelTemplate

# Import variables from src
from src.scripts.constants import PATH


class Direction(DataModelTemplate):

    json_path = '{}/data/direction.json'.format(PATH)
    objects = {}

    def __repr__(self):
        return '<Direction {}>'.format(self.id)