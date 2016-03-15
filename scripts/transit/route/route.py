
import configparser
import copy
import csv
import datetime
import os
import re
import sys

"""
GO Imports------------------------------------------------------
"""
import src.scripts.transit.constants as System
import src.scripts.transit.route.constants as Constants
import src.scripts.transit.stop.stop as st

"""
Classes----------------------------------------------------------------
"""
class Route:

    objects = {}
    header_0 = 'Name'
    header_1 = 'Stop'

    def __init__(self, rt):
        # Attributes from metadata
        self.name = rt[0]
        self.id = rt[1]
        self.description = rt[2]
        self.color = rt[3]
        self.service = rt[4]
        self.offset = rt[7]
        self.joint = rt[8]
        self.headway = rt[9]
        self.miles = rt[10]
        self.data_file = rt[11]
        
        # Attributes from conversion
        self.direction0 = Direction.objects[rt[5]].name
        self.direction1 = Direction.objects[rt[6]].name
        self.date = Service.objects[self.service].start_date
        self.start = Service.objects[self.service].start_time
        self.end = Service.objects[self.service].end_time
        self.service_text = Service.objects[self.service].text
        self.data = self.load_data()

        # Attributes from processing
        self.roundtrip = 0
        self.stop_time0 = {}
        self.stop_time1 = {}
        self.origin0 = {}
        self.origin1 = {}
        self.display = {}
        self.stop_times = {}

        # Set objects
        Route.objects[self.name] = self
        Route.objects[self.id] = self

        # Actually process records
        self.set_order('0')
        self.set_order('1')
        self.set_roundtrip()
        self.set_entries()

    def __repr__(self):
        return ('<{} was initialized '.format(self.name) +
                'with service {}'.format(self.service) +
                'and directions of {} and {}>'.format(self.direction0,
                                                      self.direction1))

    @staticmethod
    def process():
        # Load direction and service CSVs
        Direction.load()
        Service.load()

        # Old file match: re.compile('route\d*[a-zA-Z]_\d{8}\.csv')
        # Load metadata.csv
        reader = csv.reader(open(System.path + '/data/routes/metadata.csv',
                                 'r', newline=''),
                            delimiter=',', quotechar='|')

        # Initialize and process selected routes
        routes = {}
        for rt in reader:
            if rt[0] == Route.header_0:
                continue
            # Select route values for date in config
            if rt[4] in Service.select_date:
                Route(rt)
        return True
    
    def load_data(self):
        # Load data file for the route
        reader = csv.reader(open(System.path + '/data/routes/' +
                                 self.data_file, 'r', newline=''),
                            delimiter=',', quotechar='|')
        
        # Set data entries
        data = []
        for row in reader:
            if row[0] == Route.header_1:
                continue
            data.append(row)
        return data

    def set_order(self, dirnum):
        order = {}
        i = int(dirnum)
        # Set order[travel_time] = stop_id
        for entry in self.data:
            if not re.search('[a-z]', entry[i + 1]) and entry[0]:
                order[int(entry[i + 1])] = entry[0]
        # List of stop_ids in order of travel_time
        temp = [order[key] for key in sorted(order.keys())]
        # Convert temp list to dictionary of segment order
        order = {}
        i = 1
        for stop_id in temp:
            order[stop_id] = i
            i += 1
        exec('self.order{}=order'.format(dirnum))
        return True

    def set_roundtrip(self):
        self.offset0 = int(self.offset)
        for entry in self.data:
            if re.search('d', entry[1]):
                self.roundtrip += (int(re.sub('d', '', entry[1])) / 60)
                self.offset1 = (self.offset0 +
                                (int(re.sub('d', '', entry[1])) / 60)
                                 ) % int(self.headway)
            if re.search('d', entry[2]):
                self.roundtrip += (int(re.sub('d', '', entry[2])) / 60)
        return True

    def set_entries(self):
        # Set daily start and end times
        start = copy.deepcopy(self.date).replace(hour=int(self.start[:-2]),
                                                 minute=int(self.start[-2:]))
        end = copy.deepcopy(self.date).replace(hour=int(self.end[:-2]),
                                               minute=int(self.end[-2:]))

        # Handle processing for each entry
        for entry in self.data:
            # General record validation
            if entry[0] == Route.header_0:
                continue
            if not re.sub(' ', '', ''.join(str(x) for x in entry)):
                continue

            # Stop validation and mapping
            if str(entry[0]) not in st.Stop.obj_map:
                raise ValueError('Stop ' + str(entry[0]) + ' from file ' +
                                 str(self.data_file) + ' is not recognized.')
            self.display[entry[0]] = entry[4]

            # GPS reference handling
            gps_ref = re.split('&', entry[3])

            # Process entries
            self.set_stop_time((entry[0], gps_ref[0]), entry[1], start, end,
                               '0')
            self.set_stop_time((entry[0], gps_ref[1]), entry[2], start, end,
                               '1')
        # Convert origin_time value in stop_time to trip_id
        self.set_trip_ids('0')
        self.set_trip_ids('1')
        return True

    def set_stop_time(self, stop, travel_time, start, end, dirnum):
        if re.search('[a-zA-Z]', travel_time):
            return False

        # Base time is start + spread + offset
        base = start + datetime.timedelta(0, (int(travel_time) + (eval(
            'int(self.offset' + dirnum + ')') * 60)))

        # If spread + offset >= headway then reduce base by headway time
        if ((int(travel_time) / 60) + eval('int(self.offset' + dirnum + ')'
                                           ) >= int(self.headway)):
            base = base - datetime.timedelta(0, 60 * int(self.headway))

        # Add stop_times until end time
        while True:
            if base <= end:
                origin = base - datetime.timedelta(0, int(travel_time))
                if stop not in eval('self.stop_time{}'.format(dirnum)):
                    exec('self.stop_time{}[stop]=dict()'.format(dirnum))
                exec('self.stop_time{}[stop]'.format(dirnum) +
                     '[base.strftime(\'%H:%M\')]=origin.strftime(\'%H:%M\')')
                exec('self.origin{}[origin.strftime(\'%H:%M\')]=True'.format(dirnum))
            else:
                break
            base = base + datetime.timedelta(0, 60 * int(self.headway))
        return True

    def set_trip_ids(self, dirnum):
        # Convert origin_time values to trip_ids
        i = 1
        for time in sorted(eval('self.origin{}.keys()'.format(dirnum))):
            # Instantiate a Trip object
            exec('trip=Trip(self.id, self.service, Direction.convert[' +
                 'self.direction{}], i)'.format(dirnum))
            # Set origin_time to trip_id
            exec('self.origin{}[time]=trip.id'.format(dirnum))
            i += 1

        # Instantiate StopTime objects for each stop_time
        for stop in eval('self.stop_time{}'.format(dirnum)):
            for time in eval('self.stop_time{}[stop]'.format(dirnum)):
                exec('trip_id=self.origin{}[self.stop_time'.format(dirnum) +
                     '{}[stop][time]]'.format(dirnum))
                exec('StopTime(trip_id, stop[0], stop[1], time, ' +
                     'self.order{}[stop[0]], 0, '.format(dirnum) + # FIX THIS ABOUT THE TIMEPOINT TO SET FOR 100, 220, 480, 780
                     'self.display[stop[0]])')
        return True


class Direction:

    objects = {}
    convert = {}
    header_0 = 'direction_id'

    def __init__(self, ID, name, description):
        self.id = ID
        self.name = name
        self.description = description
        Direction.objects[ID] = self
        Direction.convert[name] = ID

    @classmethod
    def load(cls):
        reader = csv.reader(open(System.path + '/data/routes/direction.csv',
                            'r', newline=''), delimiter=',', quotechar='|')
        for row in reader:
            if row[0] == cls.header_0:
                continue
            cls(row[0], row[1], row[2])
        return True


class Service:

    objects = {}
    service_dates = {}
    select_date = {}
    header_0 = 'service_id'

    def __init__(self, ID, days, start_date, end_date, start_time, end_time,
                 text):
        self.ID = ID
        self.days = days
        self.start_date = datetime.datetime.strptime(start_date, '%Y%m%d')
        self.end_date = datetime.datetime.strptime(end_date, '%Y%m%d')
        self.start_time = start_time
        self.end_time = end_time
        self.text = text
        self.set_service_date()
        Service.objects[ID] = self

    @classmethod
    def load(cls):
        reader = csv.reader(open(System.path + '/data/routes/service.csv',
                            'r', newline=''), delimiter=',', quotechar='|')
        for row in reader:
            if row[0] == cls.header_0:
                continue
            days = {}
            i = 1
            while i <= 7:
                days[i] = row[i]
                i += 1
            cls(row[0], days, row[8], row[9], row[10], row[11], row[12])
        return True

    def set_service_date(self):
        if self.start_date not in Service.service_dates:
            Service.service_dates[self.start_date] = {}
        Service.service_dates[self.start_date][self.ID] = True
        # If selected date in service date range add True entry to select_date
        if self.start_date <= Constants.date <= self.end_date:
            Service.select_date[self.ID] = True
        return True


class Trip:

    objects = {}

    def __init__(self, route_id, service_id, direction_id, trip_seq):
        self.route_id = route_id
        self.service_id = service_id
        self.direction_id = direction_id
        self.trip_seq = str(hex(trip_seq))
        self.id = '-'.join([route_id, service_id, direction_id,
                             self.trip_seq])
        self.route = Route.objects[route_id].name
        self.direction = Direction.objects[direction_id].name
        self.stop_times = {}
        Trip.objects[self.id] = self

    @staticmethod
    def get_trip_id(route_id, direction_id, service_id, seq):
        if '-'.join([route_id, direction_id, service_id, str(hex(seq))]
                    ) not in Trip.objects:
            Trip(route_id, direction_id, service_id, str(hex(seq)))
        return Trip.objects[(route_id, direction_id, service_id,
                             str(hex(seq)))]

    @staticmethod
    def add_stop_time(route_id, direction_id, service_id, seq, stop_id, time):
        obj = Trip.get_trip_id(route_id, direction_id, service_id,
                               str(hex(seq)))
        obj._stop_time[(stop_id, time)] = True
        return True


class StopTime:

    objects = {}
    matrix_header = ['trip_id', 'stop_id', 'gps_ref', 'direction', 'arrival',
                     'departure', 'stop_seq', 'timepoint', 'pickup',
                     'dropoff', 'display']
    matrix = [matrix_header]

    def __init__(self, trip_id, stop_id, gps_ref, time, stop_seq, timepoint,
                 display):
        # Attributes from __init__
        self.trip_id = trip_id
        self.stop_id = stop_id
        self.gps_ref = gps_ref
        self.arrival = time
        self.departure = time
        self.time = time
        self.stop_seq = stop_seq
        self.timepoint = timepoint
        self.pickup = 0
        self.dropoff = 0
        self.display = display

        # Attributes from trip_id
        self.route = Trip.objects[trip_id].route
        self.direction = Trip.objects[trip_id].direction

        # Set records
        self.append_record()
        Trip.objects[trip_id].stop_times[stop_seq] = stop_id
        StopTime.objects[(trip_id, stop_id)] = self

    def append_record(self):
        StopTime.matrix.append([self.trip_id, self.stop_id, self.gps_ref,
                                self.direction, self.arrival, self.departure,
                                self.stop_seq, self.timepoint, self.pickup,
                                self.dropoff, self.display])
        return True

    @staticmethod
    def publish_matrix():
        if not os.path.exists(System.path + '/reports/routes'):
            os.makedirs(System.path + '/reports/routes')
        writer = csv.writer(open(System.path +
            '/reports/routes/records' +
            '.csv', 'w', newline=''), delimiter=',', quotechar='|')
        for row in StopTime.matrix:
            writer.writerow(row)
        return True


Route.process()
if __name__ == '__main__':
    StopTime.publish_matrix()
