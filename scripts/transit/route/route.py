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
from src.scripts.transit.route.constants import DATE, STOP_TIME_HEADER


class Route(object):

    objects = {}
    header_0 = 'sheet'

    def __init__(self, name, id, short, desc, color, miles, date, path, config, logo):
        # Attributes from metadata
        self.name = name
        self.id = id
        self.short = short
        self.desc = desc
        self.color = color
        self.miles = float(miles)
        self.date = date
        self.path = path
        self.logo = logo

        # Additional attributes
        self.trip_id = 1
        self.stop_times = {}
        self.dirnums = {}

        # Set objects
        Route.objects[self.id] = self

        # Load sheets from data
        self.sheets = {}
        for sheet in config:
            new_sheet = sheet + [self]
            self.sheets[Sheet(*new_sheet)] = True

    def __repr__(self):
        return '<{}>'.format(self.name)

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
                    subdirs = sorted([d for d in inner_dirnames if re.search('\d{8}', d)]) + [
                        datetime.datetime.max.strftime('%Y%m%d')]

                    # Iterate through the subdirs in order checking if the DATE is between it and the subsequent date
                    i = 0
                    while i < (len(subdirs) - 1):
                        # Only select the folder that matches the DATE query from route/constants.py
                        date0 = datetime.datetime.strptime(subdirs[i], '%Y%m%d')
                        date1 = datetime.datetime.strptime(subdirs[i + 1], '%Y%m%d')
                        if date0 <= DATE < date1:

                            # Read the data.csv file
                            data = []
                            reader = csv.reader(open('{}/{}/{}/config.csv'.format(dirpath, dirname, subdirs[i]), 'r',
                                                     newline=''), delimiter=',', quotechar='|')
                            for row in reader:
                                if row[0] == Route.header_0:
                                    continue
                                if Service.objects[row[1]].end_date < DATE:
                                    break
                                data.append(row)

                            # Create Route object
                            args = re.split(',', metadata.rstrip()) + [date0, '{}/{}/{}/'.format(dirpath, dirname,
                                                                                                 subdirs[i]), data,
                                                                       logo]
                            Route(*args)

                            # Break loop so that the correct match is the final selection
                            i = len(subdirs)

                        i += 1

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
        self.route.dirnums[dirnum] = True

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

    def __repr__(self):
        return '<Sheet object for {}>'.format(self.sheet)

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

                args = [self] + entry + [i, self.segment]
                self.segment.add_stop_seq(StopSeq(*args))

            i += 1

        # Set actual timing orders
        self.segment.set_order()

        # Set stop_times
        for stop_seq in self.segment.stop_seqs:
            self.set_stop_time(self.segment, self.segment.stop_seqs[stop_seq], self.start, self.end)

        # Set trips by converting origin_time value in stop_time to trip_id
        self.set_trip_ids()
        return True

    def set_stop_time(self, segment, stop_seq, start, end):
        # Base time is start + spread + offset
        base = start + datetime.timedelta(seconds=(stop_seq.arrive + segment.offset))

        # If spread + offset >= headway then reduce base by headway time
        if stop_seq.arrive + segment.offset >= self.headway:
            base = base - datetime.timedelta(seconds=self.headway)

        # Add stop_times until end time
        while base < end:
            origin = base - datetime.timedelta(seconds=stop_seq.arrive)

            # stop_seq.stop_times[time] = origin_time
            stop_seq.stop_times[base] = origin

            # segment.trips[origin_time] = True
            segment.trips[origin] = True

            base = base + datetime.timedelta(seconds=self.headway)
        return True

    def set_trip_ids(self):
        # For each origin time of the segment set a unique Trip id
        for time in sorted(self.segment.trips):
            # Instantiate a Trip object
            self.segment.trips[time] = Trip(self.route.id, self.service.id, self.direction.id,
                                            self.route.trip_id, self.segment)

            # Increment route's Trip id generator
            self.route.trip_id += 1

        # Instantiate StopTime objects for each stop_time
        for stop_seq in self.segment.stop_seqs:
            stop_seq = self.segment.stop_seqs[stop_seq]
            for arrive in stop_seq.stop_times:
                # Collect the trip_id based on the origin time
                trip_id = self.segment.trips[stop_seq.stop_times[arrive]].id
                depart = arrive + stop_seq.timedelta
                gtfs_depart = arrive + stop_seq.gtfs_timedelta

                # Set a StopTime object with all attributes
                StopTime(trip_id, stop_seq.stop, stop_seq.gps_ref, arrive, depart, gtfs_depart, stop_seq.order,
                         stop_seq.timed, stop_seq.display)
        return True


class JointRoute(object):

    objects = {}
    locations = {}

    def __init__(self, id):
        self.id = id
        self.sheets = {}  # {service_id: [Sheet1, Sheet2, ... , SheetN]}
        self.route_graphs = {}  # {service_id: RouteGraph}
        self.service_order = {}  # {service_id: prev service_id else None}
        self.schedule_text = ''
        self.start_time = None
        self.end_time = None
        self.headway = 0
        JointRoute.objects[id] = self

    @staticmethod
    def process():
        # Initialize JointRoute objects
        for sheet in sorted(Sheet.objects):
            sheet = Sheet.objects[sheet]

            # Set JointRoute name/id
            joint = sheet.joint

            # VALIDATE WITH JOINT.csv LATER -------------------------------------------------------------------------!!!

            # Load JointRoute object
            if joint not in JointRoute.objects:
                JointRoute(joint)
            obj = JointRoute.objects[joint]

            # Add sheet object to schedule list in JointRoute object's schedules
            if sheet.service not in obj.sheets:
                obj.sheets[sheet.service] = []
            obj.sheets[sheet.service] = obj.sheets.get(sheet.service, 0) + [sheet]

        # Iterate through JointRoute objects and process
        for joint in sorted(JointRoute.objects):
            joint = JointRoute.objects[joint]
            joint.set_service_order()
            prev = None

            # Process each service within the JointRoute object in order
            for service in joint.service_order:
                segments = [sheet.segment for sheet in joint.sheets[service]]
                joint.route_graphs[service] = RouteGraph(joint.id, service, segments, prev)
                joint.headway = joint.route_graphs[service].headway
                prev = joint.route_graphs[service]

                # After processing the RouteGraph and assigning drivers to trips
                route_graph = joint.route_graphs[service]
                for driver in route_graph.schedules:
                    # Set the correct start location for each of the drivers based on the first trip
                    trip = route_graph.schedules[driver][sorted(route_graph.schedules[driver].keys())[0]]
                    if service == joint.service_order[0]:
                        JointRoute.locations[driver] = trip.stop_times[sorted(trip.stop_times.keys())[0]]

                    # Disseminate driver values to Trip and StopTime objects
                    for trip in route_graph.schedules[driver]:
                        trip = route_graph.schedules[driver][trip]
                        trip.driver = driver
                        for seq in trip.stop_times:
                            StopTime.objects[(trip.id, seq)].driver = driver
                            StopTime.objects[(trip.id, seq)].joint = joint

        return True

    def set_service_order(self):
        services = self.sheets.keys()
        temp = sorted([(service.start_time, service) for service in services])
        self.service_order = [t[1] for t in temp]
        self.schedule_text = self.service_order[0].text
        self.start_time = self.service_order[0].start_time
        self.end_time = self.service_order[-1].end_time
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
        self.text = text

        # Handle times that are at or after midnight (24 + hour scale for GTFS)
        if int(end_time[:-2]) >= 24:
            self.end_time = copy.deepcopy(self.start_date.replace(hour=int(end_time[:-2]) - 24,
                                                                  minute=int(end_time[-2:]))) + datetime.timedelta(
                days=1)
        else:
            self.end_time = copy.deepcopy(self.start_date).replace(hour=int(end_time[:-2]), minute=int(end_time[-2:]))

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
        self.trip_seq = str(trip_seq)
        self.id = '-'.join([route_id, service_id, direction_id, self.trip_seq])
        self.route = Route.objects[route_id]
        self.direction = Direction.objects[direction_id]
        self.segment = segment
        self.stop_times = {}
        self.driver = None
        Trip.objects[self.id] = self

    def __repr__(self):
        return '<Trip for {} with service {} and direction {}>'.format(self.route.name, self.service_id,
                                                                       self.direction.name)

    @staticmethod
    def get_trip_id(route_id, direction_id, service_id, seq):
        if '-'.join([route_id, direction_id, service_id, str(hex(seq))]) not in Trip.objects:
            Trip(route_id, direction_id, service_id, str(hex(seq)))
        return Trip.objects[(route_id, direction_id, service_id, str(hex(seq)))]

    def parse(self):
        return re.split('-', self.id)


class StopTime(object):

    objects = {}

    def __init__(self, trip_id, stop_id, gps_ref, arrive, depart, gtfs_depart, stop_seq, timepoint, display):
        # Attributes from __init__
        self.trip = Trip.objects[trip_id]
        self.stop_id = stop_id
        self.gps_ref = gps_ref

        self.arrive = arrive.strftime('%H:%M:%S')
        self.depart = depart.strftime('%H:%M:%S')
        self.gtfs_depart = gtfs_depart.strftime('%H:%M:%S')
        self.arrive_24p = convert_to_24_plus_time(self.trip.segment.start, arrive)
        self.depart_24p = convert_to_24_plus_time(self.trip.segment.start, depart)
        self.gtfs_depart_24p = convert_to_24_plus_time(self.trip.segment.start, gtfs_depart)

        self.stop_seq = stop_seq
        self.timepoint = timepoint
        self.pickup = 3 if not timepoint else 0
        self.dropoff = 3 if not timepoint else 0
        self.display = display
        self.driver = 0
        self.joint = None

        # Attributes from trip_id
        self.route = self.trip.route
        self.direction = Trip.objects[trip_id].direction

        # Set records
        self.trip.stop_times[stop_seq] = stop_id
        StopTime.objects[(trip_id, stop_seq)] = self

    def get_record(self):
        return [self.trip.id, self.stop_id, self.gps_ref, self.direction.name, self.arrive, self.gtfs_depart,
                self.stop_seq, self.timepoint, self.pickup, self.dropoff, self.display, self.driver, self.joint.id]

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


def convert_to_24_plus_time(date0, date1, seconds=True):
    if date0.day != date1.day:
        if seconds:
            return ':'.join(pad_time(t) for t in [date1.hour + 24, date1.minute, date1.second])
        else:
            return ':'.join(pad_time(t) for t in [date1.hour + 24, date1.minute])
    else:
        if seconds:
            return date1.strftime('%H:%M:%S')
        else:
            return date1.strftime('%H:%M')


def convert_to_24_time(time, seconds=True):
    time = re.split(':', time)
    hour = int(time[0])
    hour %= 24
    if seconds:
        return ':'.join(pad_time(t) for t in [hour] + time[1:])
    else:
        return ':'.join(pad_time(t) for t in [hour, time[1]])


def pad_time(time_unit):
    return '0' + str(time_unit) if len(str(time_unit)) == 1 else str(time_unit)


Route.process()
JointRoute.process()
if __name__ == '__main__':
    StopTime.publish_matrix()
