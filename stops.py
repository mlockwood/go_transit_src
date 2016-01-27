
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

    begin = datetime.date(2015, 8, 31)
    finish = datetime.date(2016, 11, 30)
    baseline = 19.4000
    final = 83.3333
    increment = (final - baseline) / abs(finish - begin).days
    go_transit_path = PathSetter.find_path('go_transit')

class Stop:

    objects = {}
    obj_map = {}
    header = {}

    def __init__(self, stop_id):
        self._stop_id = stop_id
        Stop.objects[stop_id] = self

    @staticmethod
    def map_objects():
        for stop in Stop.objects:
            obj = Stop.objects[stop]
            Stop.obj_map[str(obj._stop_id)] = obj
            if obj._name:
                Stop.obj_map[obj._name] = obj
            if obj._codename:
                Stop.obj_map[str(obj._codename)] = obj
            if obj._historic:
                Stop.obj_map[obj._historic] = obj

class Point:
    
    objects = {}
    header = {}

    def __init__(self, data):
        i = 0
        while i < len(data):
            try:
                exec('self._' + str(Point.header[i]).lower() + '=' +
                     str(data[i]).lower())
                if isinstance(eval('self._' + str(Point.header[i]).lower()),
                              complex):
                    exec('self._' + str(Point.header[i]).lower() + '=\'' +
                         str(data[i]).lower() + '\'')
            except:
                exec('self._' + str(Point.header[i]).lower() + '=\'' +
                     str(data[i]).lower() + '\'')
            i += 1
        Point.objects[(str(self._stop_id), str(self._gps_ref))] = self

    @staticmethod
    def process():
        reader = csv.reader(open(System.go_transit_path +
            '/data/stops/stops.csv', 'r', newline=''), delimiter=',',
            quotechar='|')
        points = []
        for row in reader:
            points.append(row)
        
        # Set header
        i = 0
        while i < len(points[0]):
            Point.header[i] = points[0][i]
            i += 1
            
        # Initialize all other rows as objects
        stops = {}
        for data in points[1:]:
            pt = Point(data)
            if pt._stop_id not in stops:
                stops[pt._stop_id] = {}
            stops[pt._stop_id][pt] = True
            
        # Convert stop DS items to stop objects, will have a feature of data
        # iff all points for the stop have the same value for that feature
        for stop in stops:
            obj = Stop(stop)
            obj._points = stops[stop]
            for feature in Point.header.values():
                match = True
                temp = 'none'
                for pt in obj._points:
                    if temp == 'none':
                        temp = eval('pt._' + str(feature))
                    elif eval('pt._' + str(feature)) != temp:
                        match = False
                if match == True:
                    exec('obj._' + str(feature) + '= temp')

        # Develop object map for stops
        Stop.map_objects()
        return True

class Inventory:

    objects = {}

    def __init__(self, file):
        self._file = file
        self._records = {}
        Inventory.objects[self._file] = self

    @staticmethod
    def process():
        for dirpath, dirnames, filenames in os.walk(System.go_transit_path
                                                    + '/data/stops'):
            for filename in [f for f in filenames if re.search(
                'stop_inventory', f)]:
                obj = Inventory((str(dirpath) + '/' + str(filename)))
                obj.read_inventory()
        return True

    def read_inventory(self):
        reader = csv.reader(open(self._file, 'r', newline=''),
                            delimiter=',', quotechar='|')
        self._year = int(self._file[-10:-8]) + 2000
        self._month = int(self._file[-8:-6])
        self._day = int(self._file[-6:-4])
        records = []
        for row in reader:
            records.append(row)
        self._header = records[0]
        for line in records[1:]:
            self._records[line[0]] = {}
            i = 1
            while i < len(line):
                self._records[line[0]][self._header[i]] = line[i]
                i += 1
        return True
    
Point.process()
Inventory.process()
