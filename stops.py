
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

    def __init__(self, data):
        i = 0
        while i < len(data):
            try:
                exec('self._' + str(Stop.header[i]).lower() + '=' +
                     str(data[i]).lower())
                if isinstance(eval('self._' + str(Stop.header[i]).lower()),
                              complex):
                    exec('self._' + str(Stop.header[i]).lower() + '=\'' +
                         str(data[i]).lower() + '\'')
            except:
                exec('self._' + str(Stop.header[i]).lower() + '=\'' +
                     str(data[i]).lower() + '\'')
            i += 1
        Stop.objects[self._stop_id] = self
        Stop.obj_map[str(self._stop_id)] = self
        if self._name:
            Stop.obj_map[self._name] = self
        if self._codename:
            Stop.obj_map[str(self._codename)] = self
        if self._historic:
            Stop.obj_map[self._historic] = self

    @staticmethod
    def process():
        reader = csv.reader(open(System.go_transit_path +
            '/data/stops/stops.csv', 'r', newline=''), delimiter=',',
            quotechar='|')
        stops = []
        for row in reader:
            stops.append(row)
        # Set header
        i = 0
        while i < len(stops[0]):
            Stop.header[i] = stops[0][i]
            i += 1
        # Initialize all other rows as objects
        for stop in stops[1:]:
            Stop(stop)
        return True
    
Stop.process()
