#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

# Python libraries and packagesa
import copy
import datetime
import math
import re

# Entire scripts from src
from scripts.transit.stop.stop import Stop, Point
from scripts.transit.route.errors import *

# Classes and variables from src
from scripts.transit.constants import PATH
from scripts.transit.route.constants import DATE, STOP_TIME_HEADER
from scripts.utils.IOutils import load_json, export_json

from scripts.transit.route.segment import Segment, StopSeq, Direction
from scripts.transit.route.service import Service
from scripts.transit.route.trip import Trip, StopTime

# Import classes and functions from src
from scripts.utils.functions import stitch_dicts

# Import variables from src
from scripts.transit.route.constants import LAX

# Load dependent data
Point.process()
Direction.load()
Segment.load()
StopSeq.load()
Service.load()


class Route(object):

    objects = {}
    validate = {}
    header_0 = 'sheet'

    def __init__(self, name, id, short, desc, color, text_color, miles, path, config):
        # Attributes from metadata
        self.name = name
        self.id = id
        self.short = short
        self.desc = desc
        self.color = color
        self.text_color = text_color
        self.miles = float(miles)
        self.path = path

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
        return '<Route {}>'.format(self.name)


    @staticmethod
    def set_route_validation():
        for route in Route.objects:
            if route not in Route.validate:
                Route.validate[route] = {}
            for sheet in Route.objects[route].sheets:
                if (sheet.service.start_date, sheet.service.end_date) not in Route.validate[route]:
                    Route.validate[route][(sheet.service.start_date, sheet.service.end_date)] = {}
                for stop in sheet.stops:
                    Route.validate[route][(sheet.service.start_date, sheet.service.end_date)][stop] = True
        return True

    @staticmethod
    def query_validation(route, date, stop):
        if route in Route.objects:
            for key in Route.validate[route]:
                if key[0] <= date <= key[1]:
                    if stop in Route.validate[route][key].keys():
                        return True
        return False


class Sheet(object):

    def set_entries(self):
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
                                            self.segment)

            # Increment route's Trip id generator
            self.route.trip_id += 1

        # Instantiate StopTime objects for each stop_time
        for stop_seq in self.segment.stop_seqs:
            stop_seq = self.segment.stop_seqs[stop_seq]
            for arrive in stop_seq.stop_times:

                # Set a StopTime object with all attributes
                StopTime(self.segment.trips[stop_seq.stop_times[arrive]].id, stop_seq, arrive)
        return True


class Joint(object):

    objects = {}
    locations = {}

    def __init__(self, id, routes, desc, service_id, headway):
        self.id = int(id)
        self.routes = routes
        self.desc = desc
        self.service = Service.objects[int(service_id)]
        self.service_id = int(service_id)
        self.headway = int(headway)
        self.schedules = {}  # {<Schedule>: {0: <Segment>, 1: <Segment>, ... } ... }
        self.graphs = {}  # {time: RouteGraph}
        Joint.objects[int(id)] = self

    @staticmethod
    def process():

        # Process RouteGraphs for each schedule in Joint.schedules

        return True

    @classmethod
    def load(cls):
        load_json('{}/data/routes/joint.json'.format(PATH), cls)

    @classmethod
    def export(cls):
        export_json('{}/data/routes/joint.json'.format(PATH), cls)

    def get_json(self):
        return dict([(k, getattr(self, k)) for k in ['id', 'desc', 'routes', 'service_id', 'headway']])


class Schedule(object):

    objects = {}

    def __init__(self, id, joint_id, start_str, end_str, offset):
        self.id = int(id)
        self.joint_id = int(joint_id)
        self.joint = Joint.objects[joint_id]
        self.start_str = start_str
        self.end_str = end_str
        self.offset = int(offset)

        self.start = self.joint.service.start_date.replace(hour=int(start_str[:2]), minute=int(start_str[2:]))
        # Handle times that are at or after midnight (24+ hour scale for GTFS)
        if int(end_str[:2]) >= 24:
            self.end = copy.deepcopy(self.joint.service.end_date
                ).replace(hour=int(end_str[:2]) - 24, minute=int(end_str[2:])) + datetime.timedelta(days=1)
        else:
            self.end = copy.deepcopy(self.joint.service.end_date).replace(hour=int(end_str[:2]),
                                                                          minute=int(end_str[2:]))

        self.segments = self.get_segments()
        self.joint.schedules[self] = self.segments
        Schedule.objects[int(id)] = self

    def __repr__(self):
        return '<Schedule {}>'.format(self.id)

    def __str__(self):
        return '<Schedule {}>'.format(self.id)

    @classmethod
    def load(cls):
        load_json(PATH + '/data/routes/schedules.json', cls)

    @classmethod
    def export(cls):
        export_json(PATH + '/data/routes/schedules.json', cls)

    def get_json(self):
        return dict([(k, getattr(self, k)) for k in ['id', 'joint_id', 'start_str', 'end_str', 'offset']])

    def get_segments(self):
        return dict((segment.dir_order, segment) for segment in Segment.schedule_query[self.id])


class RouteGraph(object):

    objects = {}

    def __init__(self, joint, schedule, segments, prev=None):
        # Initialized attributes
        self.joint = joint
        self.schedule = schedule
        self.segments = segments  # {0: <Segment>, 1: <Segment>, 2: <Segment> ... }

        # Setup attributes
        self.roundtrip = 0
        self.prev = self.check_prev(prev)
        self.drivers = Driver.get_drivers(math.ceil(self.roundtrip / self.joint.headway)) if not prev else prev.drivers
        self.order = self.get_order()

        # Schedule attributes
        self.schedules = {}
        self.hidden_key = {}
        self.set_schedules()

        # Add to objects
        RouteGraph.objects[(joint, schedule)] = self

    def check_prev(self, prev):
        if prev:
            # If the number of driver shifts between this and the previous schedule do not match
            if len(prev.drivers) != math.ceil(self.roundtrip / self.joint.headway):
                # Raise an error because they should match
                raise JointRouteMismatchedDriverCount('JointRoute {} has mismatched driver counts for {} and {}'.format(
                    self.joint.id, self.prev.schedule, self.schedule))

        return prev

    def get_roundtrip(self):
        # Find joint roundtrip for current time schedule
        for segment in self.segments:
            self.roundtrip += segment.trip_length
        return True

    def get_order(self):
        order = {}
        for segment in self.segments:
            # Segment_key represents the next segment, which is dir_order + 1 or if the final dir_order the next is 0
            segment_key = segment + 1 if segment + 1 in self.segments else 0
            # Set dir_order as key and value
            order[segment] = segment_key
            # Set Segment object as key and value
            order[self.segments[segment]] = self.segments[segment_key]
        return order

    def get_trip_length(self, a, b):
        """

        :param a: The origin of the trip; MUST be a Segment id OR a
            StopSeq object
        :param b: The destination of the trip; MUST be a Segment id OR a
            StopSeq object
        :param order: Order for segment ordering
        :return: The trip length
        """
        trip_length = 0

        # If the origin is a StopSeq subtract the departure time from the trip_length
        if re.search('stopseq', str(a.__class__).lower()):
            trip_length -= a.depart
            a = Segment.objects[a.segment]

        # If the destination is a StopSeq add the departure time to the trip_length
        if re.search('stopseq', str(b.__class__).lower()):
            trip_length += b.depart
            b = Segment.objects[b.segment]

        # Continue traveling the order until the cur_segment and final_segment are the same
        while a != b:
            # Add current segment's trip length to the prev_trip_length
            trip_length += self.order[a].trip_length
            # Shift the cur_segment forward
            a = self.order[a]

        return trip_length % self.roundtrip

    def get_time_locations(self, origin, trips, order, minimum=True):
        time_locs = {}
        for trip in trips:

            # Add the prev_trip_length time for connected segments after the origin before this trip if applicable
            # Then set the result as the key for the travel time since the origin for the start of the trip
            stop_time = min(trip.stop_times) if minimum else max(trip.stop_times)
            time_locs[self.get_trip_length(origin, trip.segment.stop_seqs[stop_time], order)] = trip

        return time_locs

    def get_trip_order(self, trips, order):
        time_locs = self.get_time_locations(self.trips[0][0], trips, order)
        # Convert dict to list ordered by key of arrival time but value set to trip
        trip_order = []
        for key in sorted(time_locs.keys()):
            trip_order.append(time_locs[key])
        return trip_order

    def trip_start_helper(self, origin_time, cur_segment):
        while origin_time not in Segment.objects[cur_segment].trips:
            origin_time = origin_time + datetime.timedelta(seconds=Segment.objects[cur_segment].trip_length)
            cur_segment = self.order[cur_segment]

        return Segment.objects[cur_segment].trips[origin_time], origin_time

    def get_start_locs(self):
        """
        Find all of the driver starting locations; remember location is
        time from the origin and not a physical location
        :return: {start_loc: driver}
        """
        start_locs = {}
        drivers = sorted([driver.id for driver in self.drivers]) # sort driver ids
        last = self.schedule.offset  # starting position is equal to the schedule's offset
        d = 0  # index of the current driver position

        while d < len(self.drivers):
            start_locs[last] = drivers[d]
            # Increment the last location distance by the headway % the roundtrip in case the origin is passed
            last = (last + self.joint.headway) % self.roundtrip
            d += 1

        # If prev return stitched dictionary
        if self.prev:
            return self.stitch_prev(start_locs)

        # Otherwise return start_locs as-is
        return start_locs

    def stitch_prev(self, start_locs):
        # Get end_locs from prev and add closest min trip to origin + roundtrip to create the idea of a circular graph
        self.prev.end_locs[min(self.prev.end_locs) + self.prev.roundtrip] = self.prev.end_locs[min(self.prev.end_locs)]

        # Stitch A and B trips together
        stitch = stitch_dicts(self.prev.end_locs, start_locs)

        # Check for errors
        if stitch == 'Sizes incongruent problem':
            raise IncongruentSchedulesError('Joint route {} has schedules that are incongruent:'.format(self.joint) +
                                            ' {} and {}'.format(self.prev.schedule.id, self.schedule.id))

        elif stitch == 'Duplicate problem':
            raise MismatchedJointSchedulesTimingError('Joint route {} has schedules with '.format(self.joint) +
                                                      'mismatched timing likely to do significant differences in ' +
                                                      'route design: {} {}'.format(self.prev.schedule.id,
                                                                                   self.schedule.id))

        elif stitch == 'Lax problem':
            raise LaxConstraintFailureError('Joint route {} has schedules that violate the LAX '.format(self.joint) +
                                            'constraint: {} {}'.format(self.prev.schedule.id, self.schedule.id))

        return stitch

    def set_schedules(self):
        trip_starts = self.get_start_locs()

        # If previous, use stitch to reconfigure drivers
        if self.prev:
            trip_starts = self.stitch_prev(trip_starts)

        # Initialize schedule for each driver
        for position in trip_starts:
            self.schedules[position[0]] = {position[2]: position[1]}
            self.hidden_key[position[0]] = (position[1].segment.id, position[2])

        # Forward path -- (Backward path was deprecated)
        for driver in self.schedules:
            cur_segment = self.hidden_key[driver][0]  # order should always be a Segment id
            time = self.hidden_key[driver][1]
            while True:

                # Find the time to reach the next segment from the current segment
                time = time + datetime.timedelta(seconds=Segment.objects[cur_segment].trip_length)
                if time >= Segment.objects[cur_segment].end:
                    break

                # Find the next segment from the current segment
                cur_segment = self.order[cur_segment]

                # Convert time to trip id from next segment
                # self.schedules[driver][time] = Trip
                self.schedules[driver][time] = Segment.objects[cur_segment].trips[time]


class Driver:

    objects = {}
    id_generator = 1

    def __init__(self):
        self.id = Driver.id_generator
        Driver.id_generator += 1
        Driver.objects[self.id] = self

    @staticmethod
    def get_drivers(n):
        return [Driver() for driver in range(n)]


Joint.load()
Schedule.load()
Joint.process()
# Joint.export()

