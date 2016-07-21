import csv
import os
import re

import multiprocessing as mp

"""
GO Imports------------------------------------------------------
"""

from src.scripts.transit.stop.errors import *
from src.scripts.utils.IOutils import load_json, export_json
from src.scripts.transit.constants import PATH


class Stop(object):

    objects = {}
    locations = {}

    def __init__(self, stop, name, location, description, geography, lat, lng, signage, shelter, operating, speed,
                 available):
        self.id = stop
        self.name = name
        self.location = location
        self.description = description
        self.geography = geography
        self.lat = lat
        self.lng = lng
        self.signage = signage
        self.shelter = shelter
        self.operating = operating
        self.speed = speed
        self.available = available
        Stop.objects[stop] = self
        if location not in Stop.locations:
            Stop.locations[location] = {}
        Stop.locations[location][stop[3]] = self

    @classmethod
    def load(cls):
        load_json('{}/data/stop.json'.format(PATH), cls)

    @classmethod
    def export(cls):
        export_json('{}/data/stop.json'.format(PATH), cls)


class Geography(object):

    objects = {}

    def __init__(self, id, name, minimum, maximum):
        self.id = id
        self.name = name
        self.minimum = minimum
        self.maximum = maximum
        Geography.objects[id] = self

    @classmethod
    def load(cls):
        load_json('{}/data/geography.json'.format(PATH), cls)

    @classmethod
    def export(cls):
        export_json('{}/data/geography.json'.format(PATH), cls)


class Inventory(object):

    objects = {}
    tags = {}
    order = ['g', 'f', 'a', 's', 'd', 'i', 'u', 'p', 'n']

    def __init__(self, file):
        self.file = file
        self.records = {}
        self.tags = {}
        Inventory.objects[self.file] = self

    @staticmethod
    def process():
        Inventory.load_codes()
        for dirpath, dirnames, filenames in os.walk(PATH + '/data/stops'):
            for filename in [f for f in filenames if re.search('stop_inventory', f)]:
                obj = Inventory((str(dirpath) + '/' + str(filename)))
                obj.read_inventory()
                # obj.write_report()
        return True

    @staticmethod
    def load_codes():
        reader = open(PATH + '/data/inventory_codes.txt',
                      'r')
        for line in reader:
            line = line.rstrip()
            line = re.split('-', line)
            Inventory.tags[line[0].lower()] = line[1]

    def read_inventory(self):
        reader = csv.reader(open(self.file, 'r', newline=''),
                            delimiter=',', quotechar='|')
        self.year = int(self.file[-10:-8]) + 2000
        self.month = int(self.file[-8:-6])
        self.day = int(self.file[-6:-4])
        records = []
        for row in reader:
            records.append(row)
        for line in records[1:]:
            self.records[(line[0], line[1])] = line[2]
            if line[2] not in self.tags:
                self.tags[line[2]] = {}
            self.tags[line[2]][(line[0], line[1])] = True
        return True

    def write_report(self):
        if not os.path.exists(PATH + '/reports/stops/inventory'):
            os.makedirs(PATH + '/reports/stops/inventory')
        writer = open(PATH + '/reports/stops/inventory/Inventory_' +
                      'Report_' + str(self.year) + str(self.month) +
                      str(self.day), 'w')
        for tag in Inventory.order:
            if tag in self.tags:
                writer.write(Inventory.tags[tag] + '\n')
                i = 0
                for stop in sorted(self.tags[tag].keys()):
                    writer.write(stop[0] + stop[1])
                    i += 1
                    if i != len(self.tags[tag]):
                        writer.write(', ')
                    if i % 10 == 0:
                        writer.write('\n')
                writer.write('\n\n')
        writer.close()


Stop.load()

if __name__ == '__main__':
    Geography.load()
