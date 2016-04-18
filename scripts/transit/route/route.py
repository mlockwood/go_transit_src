#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

# Python libraries and packages
import copy
import csv
import datetime
import math
import os
import re

# Entire scripts from src
import src.scripts.transit.stop.stop as st
import src.scripts.transit.route.errors as RouteErrors

# Classes and variables from src
from src.scripts.transit.constants import PATH
from src.scripts.transit.route.route_graph import StopSeq, Segment, RouteGraph
from src.scripts.transit.route.constants import DATE, LAX, STOP_TIME_HEADER


class Route(object):

    objects = {}
    header_0 = 'sheet'

    def __init__(self, name, id, desc, color, miles, date, path, config):
        # Attributes from metadata
        self.name = name
        self.id = id
        self.desc = desc
        self.color = color
        self.miles = float(miles)
        self.date = date
        self.path = path

        # Additional attributes
        self.trip_id = 1
        self.stop_times = {}

        # Set objects
        Route.objects[self.name] = self
        Route.objects[self.id] = self

        # Load sheets from data
        self.sheets = {}
        for sheet in config:
            new_sheet = sheet + [self]
            self.sheets[Sheet(*new_sheet)] = True

    def __repr__(self):
        return ('<{} was initialized with service {} and directions of '.format(self.name, self.service) +
                '{} and {}>'.format(self.direction0.name, self.direction1.name))

    @staticmethod
    def process():
        # Load direction and service CSVs
        Direction.load()
        Service.load()

        # Search for route directories in go/data/routes
        for dirpath, dirnames, filenames in os.walk(PATH + '/data/routes'):
            # Only explore subdirectories that match the route{X} format
            for dirname in [d for d in dirnames if re.search('route[\d]*', d)]:

                # Note metadata and logo paths
                with open('{}/{}/metadata.txt'.format(dirpath, dirname), 'r') as f:
                    metadata = f.read()
                logo = '{}/{dirname}/{dirname}_logo.jpg'.format(dirpath, dirname=dirname)

                # Search for YYYYMMDD file collections/subdirectories within the /route{X} subdirectory
                for inner_dirpath, inner_dirnames, inner_filenames in os.walk('{}/{}'.format(dirpath, dirname)):
                    # Only explore subdirectories that match the YYYYMMDD format
                    for inner_dirname in sorted([d for d in inner_dirnames if re.search('\d{8}', d)]):
                        # Only select the folder that matches the date query from route/constants.py
                        date = datetime.datetime.strptime(inner_dirname, '%Y%m%d')
                        if date >= DATE:

                            # Read the data.csv file
                            data = []
                            reader = csv.reader(open('{}/{}/{}/config.csv'.format(dirpath, dirname, inner_dirname), 'r',
                                                     newline=''), delimiter=',', quotechar='|')
                            for row in reader:
                                if row[0] == Route.header_0:
                                    continue
                                data.append(row)

                            # Create Route object
                            args = re.split(',', metadata.rstrip()) + [date, '{}/{}/{}/'.format(dirpath, dirname,
                                                                                                inner_dirname), data]
                            Route(*args)

                            # Break loop so that first match >= constant date is the final selection
                            break

        return True


class Sheet(object):

    objects = {}
    header_0 = 'stop'

    def __init__(self, sheet, service, dirnum, direction, headway, offset, joint, route):
        # Attributes from data.csv
        self.sheet = sheet
        self.service = Service.objects[service]
        self.dirnum = dirnum
        self.direction = Direction.objects[direction]
        self.headway = int(headway)
        self.offset = int(offset)
        self.joint = joint
        self.route = route

        # Set objects
        Sheet.objects[(sheet, route.id, self.service.id, self.direction.id)] = self

        # Attributes from conversion
        self.date = self.route.date
        self.start = self.service.start_time
        self.end = self.service.end_time
        self.service_text = self.service.text
        self.data = self.load_data()

        # Set a Segment object for the sheet
        self.segment = Segment(route, self)

        # Process
        self.set_entries()

    def load_data(self):
        # Load data file for the route
        reader = csv.reader(open('{}{}'.format(self.route.path, self.sheet), 'r', newline=''), delimiter=',',
                            quotechar='|')

        # Set data entries
        data = []
        i = 0
        for row in reader:
            if row[0].lower() == Sheet.header_0:
                continue
            data.append(row)

            i += 1
        return data

    def set_entries(self):
        i = 0
        # Set segment's order[travel_time] = stop_id
        for entry in self.data:

            # General record validation
            if not re.sub(' ', '', ''.join(str(x) for x in entry)):
                continue

            # Stop validation and mapping
            if (entry[0], entry[1]) not in st.Point.objects:
                raise RouteErrors.UnknownStopPointError('Stop {}{} from file {} is not recognized.'.format(entry[0],
                                                                                                           entry[1],
                                                                                                           self.sheet))

            # Create and process stop_seq objects if there is a stop_id and valid arrival
            if entry[2] and not re.search('n', entry[2]):

                # Origin handling
                if re.search('a', entry[2]):
                    self.segment.origin = (entry[0], entry[1])

                # Destination handling
                if re.search('d', entry[3]):
                    self.segment.destination = (entry[0], entry[1])
                    self.segment.trip_length = int(re.sub('d', '', entry[3]))

                args = [self.sheet] + entry + [i]
                self.segment.add_stop_seq(StopSeq(*args))

            i += 1

        # Set actual timing orders
        self.segment.set_order()

        # Set stop_times
        for stop_seq in self.segment.stop_seqs:
            self.set_stop_time(self.segment, stop_seq, self.start, self.end)

        # Set trips by converting origin_time value in stop_time to trip_id
        self.set_trip_ids()
        return True

    def set_stop_time(self, segment, stop_seq, start, end):
        # Base time is start + spread + offset
        base = start + datetime.timedelta(0, (stop_seq.arrive + (segment.offset * 60)))

        # If spread + offset >= headway then reduce base by headway time
        if (stop_seq.arrive / 60) + segment.offset >= int(self.headway):
            base = base - datetime.timedelta(0, 60 * int(self.headway))

        # Add stop_times until end time
        while True:
            if base < end:
                origin = base - datetime.timedelta(0, int(stop_seq.arrive))

                # stop_seq.stop_times[time] = origin_time
                stop_seq.stop_times[base] = origin

                # segment.origin_times[origin_time] = True
                segment.origin_times[origin] = True

            else:
                break

            base = base + datetime.timedelta(0, 60 * int(self.headway))
        return True

    def set_trip_ids(self):
        # For each origin time of the segment set a unique Trip id
        for time in sorted(self.segment.origin_times):
            # Instantiate a Trip object
            self.segment.origin_times[time] = Trip(self.route.id, self.service.id, self.direction.id,
                                                   self.route.trip_id, self.segment)

            # If time is <= self.start the trip is a starting trip for the schedule
            if time <= self.start:
                self.segment.start_trips.append(self.segment.origin_times[time])

            # Increment route's Trip id generator
            self.route.trip_id += 1

        # Instantiate StopTime objects for each stop_time
        for stop_seq in self.segment.stop_seqs:
            for arrive in stop_seq.stop_times:
                # Collect the trip_id based on the origin time
                trip_id = self.segment.origin_times[stop_seq.stop_times[arrive]].id
                depart = arrive + stop_seq.timedelta

                # Set a StopTime object with all attributes
                StopTime(trip_id, stop_seq.stop, stop_seq.gps_ref, arrive, depart, stop_seq.order, stop_seq.timed,
                         stop_seq.display)
        return True


class JointRoute(object):

    objects = {}

    def __init__(self, joint):
        self.joint = joint
        self.sheets = {}  # {service_id: [Sheet1, Sheet2, ... , SheetN]}
        self.route_graphs = {}  # {service_id: RouteGraph}
        self.service_order = {}  # {service_id: prev service_id else None}
        JointRoute.objects[joint] = self

    @staticmethod
    def process():
        # Initialize JointRoute objects
        for sheet in sorted(Sheet.objects):
            sheet = Sheet.objects[sheet]

            # Set JointRoute name/id
            joint = sheet.joint
            if joint == '<null>':
                joint = Sheet.objects[sheet].route

            # Load JointRoute object
            if joint not in JointRoute.objects:
                JointRoute(joint)
            obj = JointRoute.objects[joint]

            # Add sheet object to schedule list in JointRoute object's schedules
            if sheet.service not in obj.sheets:
                obj.sheets[sheet.service] = []
            obj.sheets[sheet.service] = obj.sheets.get(sheet.service, 0) + [sheet]

        # Iterate through JointRoute objects and process
        for joint in JointRoute.objects:
            joint = JointRoute.objects[joint]
            joint.set_service_order()
            prev = None

            # Process each service within the JointRoute object in order
            for service in joint.service_order:
                segments = [sheet.segment for sheet in joint.sheets[service]]
                joint.route_graphs[service] = RouteGraph(joint.joint, service, segments, prev)
                prev = joint.route_graphs[service]

                # After processing the RouteGraph and assigning drivers to trips
                obj = joint.route_graphs[service]
                for driver in obj.schedules:
                    # Set the correct start location for each of the drivers based on the first trip
                    obj.locations[driver] = Trip.objects[obj.hidden_key[driver]].stop_times[sorted(
                        Trip.objects[obj.hidden_key[driver]].stop_times)[0]]

                    # Disseminate driver values to Trip and StopTime objects
                    for trip in obj.schedules[driver]:
                        trip.driver = driver
                        for seq in trip.stop_times:
                            StopTime.objects[(trip.id, seq)].driver = driver.id
                            StopTime.objects[(trip.id, seq)].joint = joint.joint

        return True

    def set_service_order(self):
        services = self.sheets.keys()
        temp = sorted([(service.start_time, service) for service in services])
        self.service_order = [t[1] for t in temp]
        return True


class Direction(object):

    objects = {}
    convert = {}
    header_0 = 'direction_id'

    def __init__(self, id, name, description, origin, destination):
        self.id = id
        self.name = name
        self.description = description
        self.origin = origin
        self.destination = destination
        Direction.objects[id] = self
        Direction.convert[name] = id

    @classmethod
    def load(cls):
        reader = csv.reader(open(PATH + '/data/routes/direction.csv', 'r', newline=''), delimiter=',', quotechar='|')
        for row in reader:
            if row[0] == cls.header_0:
                continue
            cls(*row)
        return True


class Service(object):

    objects = {}
    service_dates = {}
    select_date = {}
    header_0 = 'service_id'

    def __init__(self, id, monday, tuesday, wednesday, thursday, friday, saturday, sunday, start_date, end_date,
                 start_time, end_time, text):
        self.id = id
        self.monday = monday
        self.tuesday = tuesday
        self.wednesday = wednesday
        self.thursday = thursday
        self.friday = friday
        self.saturday = saturday
        self.sunday = sunday
        self.start_date = datetime.datetime.strptime(start_date, '%Y%m%d')
        self.end_date = datetime.datetime.strptime(end_date, '%Y%m%d')
        self.start_time = copy.deepcopy(self.start_date).replace(hour=int(start_time[:-2]), minute=int(start_time[-2:]))
        self.end_time = copy.deepcopy(self.start_date).replace(hour=int(end_time[:-2]), minute=int(end_time[-2:]))
        self.text = text
        self.set_service_date()
        Service.objects[id] = self

    @classmethod
    def load(cls):
        reader = csv.reader(open(PATH + '/data/routes/service.csv',
                            'r', newline=''), delimiter=',', quotechar='|')
        for row in reader:
            if row[0] == cls.header_0:
                continue
            cls(*row)
        return True

    def set_service_date(self):
        if self.start_date not in Service.service_dates:
            Service.service_dates[self.start_date] = {}
        Service.service_dates[self.start_date][self.id] = True
        # If selected date in service date range add True entry to select_date
        if self.start_date <= DATE <= self.end_date:
            Service.select_date[self.id] = True
        return True


class Trip(object):

    objects = {}

    def __init__(self, route_id, service_id, direction_id, trip_seq, segment=None):
        self.route_id = route_id
        self.service_id = service_id
        self.direction_id = direction_id
        self.trip_seq = str(hex(trip_seq))
        self.id = '-'.join([route_id, service_id, direction_id, self.trip_seq])
        self.route = Route.objects[route_id]
        self.direction = Direction.objects[direction_id]
        self.segment = segment
        self.stop_times = {}
        Trip.objects[self.id] = self

    @staticmethod
    def get_trip_id(route_id, direction_id, service_id, seq):
        if '-'.join([route_id, direction_id, service_id, str(hex(seq))]) not in Trip.objects:
            Trip(route_id, direction_id, service_id, str(hex(seq)))
        return Trip.objects[(route_id, direction_id, service_id, str(hex(seq)))]

    def parse(self):
        return re.split('-', self.id)


class StopTime(object):

    objects = {}

    def __init__(self, trip_id, stop_id, gps_ref, arrive, depart, stop_seq, timepoint, display):
        # Attributes from __init__
        self.trip_id = trip_id
        self.stop_id = stop_id
        self.gps_ref = gps_ref
        self.arrive = arrive.strftime('%H:%M:%S')
        self.depart = depart.strftime('%H:%M:%S')
        self.stop_seq = stop_seq
        self.timepoint = timepoint
        self.pickup = 3
        self.dropoff = 3
        self.display = display
        self.driver = 0
        self.joint = None

        # Attributes from trip_id
        self.route = Trip.objects[trip_id].route
        self.direction = Trip.objects[trip_id].direction

        # Set records
        Trip.objects[trip_id].stop_times[stop_seq] = stop_id
        StopTime.objects[(trip_id, stop_seq)] = self

    def get_record(self):
        return [self.trip_id, self.stop_id, self.gps_ref, self.direction.name, self.arrive, self.depart, self.stop_seq,
                self.timepoint, self.pickup, self.dropoff, self.display, self.driver]

    @staticmethod
    def publish_matrix():
        if not os.path.exists(PATH + '/reports/routes'):
            os.makedirs(PATH + '/reports/routes')
        writer = csv.writer(open('{}/reports/routes/records.csv'.format(PATH), 'w', newline=''), delimiter=',',
                            quotechar='|')
        writer.writerow(STOP_TIME_HEADER)
        for stop_time in sorted(StopTime.objects):
            writer.writerow(StopTime.objects[stop_time].get_record())
        return True


Route.process()
JointRoute.process()
if __name__ == '__main__':
    StopTime.publish_matrix()
