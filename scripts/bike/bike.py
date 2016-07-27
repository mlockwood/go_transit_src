#!/usr/bin/env python3.4
# -*- coding: utf-8 -*-

"""
__authors__ = MichaelLockwood
__projectclass__ = go
__projectsubclass__ = bike
__projectnumber__ = 1
__projectname__ = bike.py
__date__ = February2016
__credits__ = None
__collaborators__ = None

Explanation here.
"""

from src.scripts.utils.classes import DataModelTemplate
from src.scripts.constants import PATH


class Asset(DataModelTemplate):

    json_path = '{}/data/asset.json'.format(PATH)
    objects = {}


class Bike(DataModelTemplate):

    json_path = '{}/data/bike.json'.format(PATH)
    objects = {}


class Fleet(DataModelTemplate):

    json_path = '{}/data/fleet.json'.format(PATH)
    objects = {}


class BikeGPS(DataModelTemplate):

    json_path = '{}/data/bike_gps.json'.format(PATH)
    objects = {}


class Lock(DataModelTemplate):

    json_path = '{}/data/lock.json'.format(PATH)
    objects = {}


Asset.load()
Asset.print_stats()
Bike.load()
Bike.print_stats()
Fleet.load()
Fleet.print_stats()
BikeGPS.load()
BikeGPS.print_stats()
Lock.load()
Lock.print_stats()