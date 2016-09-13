#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

# Import classes and functions from src
from src.scripts.utils.classes import DataModelTemplate

# Import variables from src
from src.scripts.constants import *


class Direction(DataModelTemplate):

    json_path = '{}/route/direction.json'.format(DATA_PATH)
    objects = {}

    def __repr__(self):
        return '<Direction {}>'.format(self.id)