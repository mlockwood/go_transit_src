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

# Import packages
import configparser
import csv
import datetime
import os
import re
import sys
import xlsxwriter

import multiprocessing as mp

"""
Closed Classes----------------------------------------------------------
"""
class PathSetter:

    @staticmethod
    def set_pythonpath(directory='', subdirectory=''):
        if directory:
            directory = PathSetter.find_path(directory)
            if subdirectory:
                if directory[-1] != '/' and subdirectory[0] != '/':
                    directory += '/'
                directory += subdirectory
        else:
            directory = os.getcwd()
        sys.path.append(directory)
        return True

    @staticmethod
    def find_path(directory):
        match = re.search('/|\\' + str(directory), os.getcwd())
        if not match:
            raise IOError(str(directory) + 'is not in current working ' +
                          'directory')
        return os.getcwd()[:match.span()[0]] + '/' + directory

"""
GO Transit Imports------------------------------------------------------
"""
PathSetter.set_pythonpath()

"""
Main Classes------------------------------------------------------------
"""
class System:

    x = 2 #index for tag
    
    @staticmethod
    def load_config():
        config = configparser.ConfigParser()
        config.read('config/system.ini')
        for var in config['DEFAULT']:
            try:
                exec('System.' + var + ' = ' + eval('\'' +
                    eval('config[\'DEFAULT\'][\'' + var + '\']') + '\''))
                if isinstance('System.' + var, complex):
                    exec('System.' + var + ' = \'' + eval(
                        'config[\'DEFAULT\'][\'' + var + '\']') + '\'')
            except:
                exec('System.' + var + ' = \'' + eval(
                    'config[\'DEFAULT\'][\'' + var + '\']') + '\'')
        return True

    @staticmethod
    def load_classes():
        Asset.load()
        Bike.load()
        GPS.load()
        Lock.load()
        BikeFixture.load()
        for obj in Bike.objects:
            Bike.objects[obj].set_current()
        Bike.print()

System.load_config()

class Asset:

    objects = {}

    def __init__(self, AID, asset):
        self._AID = AID
        self._asset = asset
        self._racks = {}
        Asset.objects[AID] = self

    @staticmethod
    def load():
        reader = csv.reader(open(System.path + '/data/bike_assets/asset.csv',
            'r', newline=''), delimiter=',', quotechar='|')
        for row in reader:
            if re.search('ID', row[0]):
                continue
            Asset(row[0], row[1])

class Bike:

    objects = {}
    fixtures = ['gps', 'locks']

    def __init__(self, BID, serial, low_step):
        self._BID = BID
        self._serial = serial
        self._low_step = low_step
        self._gps = []
        self._locks = []
        self._racks = []
        Bike.objects[BID] = self

    @staticmethod
    def load():
        reader = csv.reader(open(System.path + '/data/bike_assets/bike.csv',
            'r', newline=''), delimiter=',', quotechar='|')
        for row in reader:
            if re.search('ID', row[0]):
                continue
            Bike(row[0], row[1], row[2])

    def set_current(self):
        for F in Bike.fixtures:
            exec('self._{F}=sorted(self._{F})'.format(F=F))
            i = len(eval('self._{F}'.format(F=F))) - 1
            while i >= 0:
                if (eval('self._{F}[i][{x}]'.format(F=F, x=System.x)) == 'a' or
                    eval('self._{F}[i][{x}]'.format(F=F, x=System.x)) == 'i'):
                    exec('self._cur_{F}=self._{F}[i]'.format(F=F))
                    break
                i -= 1
        return True
        

    def print():
        for B in sorted(Bike.objects.keys()):
            print('\n', B)
            for F in Bike.fixtures:
                try:
                    print(eval('Bike.objects[B]._cur_{F}'.format(F=F)))
                except AttributeError:
                    pass
        return True

class GPS:

    objects = {}

    def __init__(self, GID, wimm):
        self._GID = GID
        self._wimm = wimm
        self._bikes = []
        GPS.objects[GID] = self

    @staticmethod
    def load():
        reader = csv.reader(open(System.path +
            '/data/bike_assets/bike_gps.csv', 'r', newline=''),
            delimiter=',', quotechar='|')
        for row in reader:
            if re.search('ID', row[0]):
                continue
            GPS(row[0], row[1])

class Lock:

    objects = {}

    def __init__(self, LID, serial):
        self._LID = LID
        self._serial = serial
        self._bikes = []
        Lock.objects[LID] = self

    @staticmethod
    def load():
        reader = csv.reader(open(System.path + '/data/bike_assets/lock.csv',
            'r', newline=''), delimiter=',', quotechar='|')
        for row in reader:
            if re.search('ID', row[0]):
                continue
            Lock(row[0], row[1])

"""
Relationship Classes----------------------------------------------------
"""
class BikeFixture:
    """
    A fixture is an item which is generally always tied to a bike which
    includes the GPS and lock.
    """

    objects = {}
    transfers = {}

    def __init__(self, BID, XID):
        self._BID = BID
        self._XID = XID
        self._records = {} # (year, month, day, tag)
        BikeFixture.objects[(BID, XID)] = self

    def load():
        reader = csv.reader(open(System.path +
            '/data/bike_assets/bike_fixture.csv', 'r', newline=''),
            delimiter=',', quotechar='|')
        for row in reader:
            if re.search('ID', row[0]):
                continue
            BikeFixture.set_bike_fixture(row[0], row[1], row[2], row[3],
                                         row[4], row[5])
            """
            # If the tag == 't', set a copy of the record aside
            if row[5] == 't':
                BikeFixture.transfers[datetime.date(row[2], row[3], row[4])
                    ] = row[1]
            """
        # BikeFixture.set_transfers()
        return True

    @staticmethod
    def set_bike_fixture(BID, XID, year, month, day, tag):
        date = datetime.date(int(year), int(month), int(day))
        # Add (bike, asset) record to BikeAsset object
        if (BID, XID) not in BikeFixture.objects:
            BikeFixture(BID, XID)
        BikeFixture.objects[(BID, XID)]._records[date] = tag
        # Join information to Bike and X(Fixture) classes
        # GPS
        if re.search('g', XID.lower()):
            Bike.objects[BID]._gps.append([date, XID, tag])
            GPS.objects[XID]._bikes.append([date, BID, tag])
        # Locks
        elif re.search('l', XID.lower()):
            Bike.objects[BID]._locks.append([date, XID, tag])
            Lock.objects[XID]._bikes.append([date, BID, tag])
        return True

    @staticmethod
    def set_transfers():
        for T in sorted(BikeFixture.transfers.keys()):
            # GPS
            if re.search('g', BikeFixture.transfers[T].lower()):
                return True
        return True
                



System.load_classes()
