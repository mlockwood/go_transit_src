
import configparser
import csv
import datetime
import math
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
import route as rt

"""
Main Classes------------------------------------------------------------
"""
class System:
    
    @staticmethod
    def load_config():
        config = configparser.ConfigParser()
        config.read('system.ini')
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

System.load_config()

class Route:

    objects = {}

    def __init__(self, data):
        for attr in data:
            try:
                exec('self.' + attr[0] + '=' + attr[1])
                if isinstance(eval('self.' + attr[0], complex)):
                    exec('self.' + attr[0] + '=\'' + attr[1] + '\'')
            except:
                try:
                    exec('self.' + attr[0] + '=\'' + attr[1] + '\'')
                except:
                    exec('self.' + attr[0] + '=[' + ','.join(
                        str(i) for i in attr[1]) + ']')
        self._date = datetime.datetime(int(self._year), int(self._month),
                                       int(self._day), 0, 0)
        Route.objects[self._route] = self

    @staticmethod
    def set_routes():
        for route in rt.Route.objects:
            data = []
            for attr in dir(rt.Route.objects[route]):
                if (attr[0:2] != '__' and attr[0] == '_' and
                    attr != '_records' and attr != '_date'):
                    data.append((attr, eval('rt.Route.objects[route].' +
                                            attr)))
            Route(data)

class Driver:

    salary = 0
    wage = 0
    benefit = 1.0
    rate = 0.0

    @staticmethod
    def set_average_wage():
        Driver.avg_wage = (Driver.wage * (((Driver.benefit - 1) * Driver.rate)
            + 1))
        return True

class Vehicle:

    lease = 0
    mile = 0.0

class Finance:

    cost_types = ['wages', 'lease', 'miles']
    header = ['route', 'base_minutes', 'wage_minutes', 'drivers', 'miles',
              'roundtrip', 'monthly_wages', 'monthly_miles', 'monthly_lease',
              'monthly_total', 'annual_wages', 'annual_miles', 'annual_lease',
              'annual_total']
    month = {1: 4, 2: 5, 3: 4, 4: 4, 5: 4, 6: 4, 7: 5}
    year = {1: 47, 2: 51, 3: 51, 4: 51, 5: 51, 6: 51, 7: 51} # removed holidays

    @staticmethod
    def load_config():
        # Driver config
        config = configparser.ConfigParser()
        config.read('driver.ini')
        d = ['salary', 'wage', 'benefit', 'rate']
        for var in d:
            exec('Driver.' + var + '= float(config[\'DRIVER\'][\'' + var +
                 '\'])')
        config = configparser.ConfigParser()
        
        # Vehicle config
        config.read('vehicle.ini')
        v = ['lease', 'mile']
        for var in v:
            exec('Vehicle.' + var + '= float(config[\'VEHICLE\'][\'' + var +
                 '\'])')
        return True

    @staticmethod
    def calc_costs():
        for route in Route.objects:
            obj = Route.objects[route]
            
            # Set base amounts
            time = (obj._date.replace(hour=int(obj._end[:-2])) -
                     obj._date.replace(hour=int(obj._start[:-2])))
            obj._base_minutes = divmod(time.days * 86400 + time.seconds, 60)[0]
            obj._wage_minutes = obj._base_minutes + (math.floor(
                obj._base_minutes / 481) * 30) + 30
            
            # Set daily costs
            obj._wage_costs = ((obj._wage_minutes / 60) * Driver.avg_wage *
                int(obj._drivers))
            obj._mile_costs = (obj._base_minutes / int(obj._roundtrip) *
                float(obj._miles) * Vehicle.mile) * int(obj._drivers)
            print(obj._route, obj._mile_costs)

            # Set monthly costs
            obj._monthly_wages = 0
            obj._monthly_lease = Vehicle.lease * int(obj._drivers)
            obj._monthly_miles = 0
            obj._monthly_total = 0
            for dow in obj._weekdays:
                obj._monthly_wages += (obj._wage_costs * Finance.month[dow])
                obj._monthly_miles += (obj._mile_costs * Finance.month[dow])
            for ct in Finance.cost_types:
                obj._monthly_total += eval('obj._monthly_' + ct)

            # Set annual costs
            obj._annual_wages = 0
            obj._annual_lease = Vehicle.lease * int(obj._drivers) * 12
            obj._annual_miles = 0
            obj._annual_total = 0
            for dow in obj._weekdays:
                obj._annual_wages += (obj._wage_costs * Finance.year[dow])
                obj._annual_miles += (obj._mile_costs * Finance.year[dow])
            for ct in Finance.cost_types:
                obj._annual_total += eval('obj._annual_' + ct)

        return True

    @staticmethod
    def report():
        Route.set_routes()
        Finance.load_config()
        Driver.set_average_wage()
        Finance.calc_costs()

        # Create CSV
        if not os.path.exists(System.path + '/reports/finance/estimates'):
            os.makedirs(System.path + '/reports/finance/estimates')
        writer = csv.writer(open(System.path +
            '/reports/finance/estimates/system.csv' , 'w', newline=''),
            delimiter=',', quotechar='|')
        writer.writerow(eval('[\'' + '\',\''.join(re.sub('_', ' ', i
            ).title() for i in Finance.header) + '\']'))

        # For each route, write to output
        for route in sorted(Route.objects):
            row = []
            for col in Finance.header:
                row.append(eval('Route.objects[route]._' + col))
            writer.writerow(row)
            
Finance.report()
