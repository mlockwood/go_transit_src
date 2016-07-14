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
        self.schedules = {}
        Joint.objects[int(id)] = self

    def __repr__(self):
        return '<Joint {}>'.format(self.id)

    @staticmethod
    def process():
        for obj in Joint.objects:
            joint = Joint.objects[obj]
            # Create trips for each schedule in order
            prev = None
            for schedule in sorted(joint.schedules.keys()):
                schedule.prev = schedule.check_prev(prev)
                schedule.drivers = Driver.get_drivers(math.ceil(schedule.roundtrip / joint.headway)
                                                      ) if not prev else prev.drivers
                schedule.set_trips()
                prev = schedule

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
        # Handle times that are at or after midnight (24+ hour scale for GTFS) remember to use start_date for end
        if int(end_str[:2]) >= 24:
            self.end = copy.deepcopy(self.joint.service.start_date
                ).replace(hour=int(end_str[:2]) - 24, minute=int(end_str[2:])) + datetime.timedelta(days=1)
        else:
            self.end = copy.deepcopy(self.joint.service.start_date).replace(hour=int(end_str[:2]),
                                                                            minute=int(end_str[2:]))

        self.prev = None
        self.drivers = []
        self.trips = {}
        self.segments = self.get_segments()
        self.roundtrip = self.get_roundtrip()
        self.order = self.get_order()
        self.joint.schedules[self] = True
        self.end_locs = {}

        Schedule.objects[int(id)] = self

    def __repr__(self):
        return '<Schedule {}>'.format(self.id)

    def __str__(self):
        return '<Schedule {}>'.format(self.id)

    def __lt__(self, other):
        return (self.start, self.end) < (other.start, other.end)

    def __le__(self, other):
        return (self.start, self.end) <= (other.start, other.end)

    def __eq__(self, other):
        return (self.start, self.end) == (other.start, other.end)

    def __ne__(self, other):
        return (self.start, self.end) != (other.start, other.end)

    def __gt__(self, other):
        return (self.start, self.end) > (other.start, other.end)

    def __ge__(self, other):
        return (self.start, self.end) >= (other.start, other.end)

    def __hash__(self):
        return hash((self.start, self.end))

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

    def check_prev(self, prev):
        if prev:
            # If the number of driver shifts between this and the previous schedule do not match
            if len(prev.drivers) != math.ceil(self.roundtrip / self.joint.headway):
                # Raise an error because they should match
                raise JointRouteMismatchedDriverCount('JointRoute {} has mismatched driver counts for {} and {}'.format(
                    self.joint.id, self.prev.id, self.id))

        return prev

    def get_roundtrip(self):
        # Find joint roundtrip for current time schedule
        roundtrip = 0
        for segment in self.segments:
            roundtrip += self.segments[segment].trip_length
        return roundtrip

    def get_order(self):
        order = {}
        for segment in self.segments:
            # Segment_key represents the next segment, which is dir_order + 1 or if the final dir_order the next is 0
            segment_key = segment + 1 if segment + 1 in self.segments else 0
            # Set dir_order as key and value
            # order[segment] = segment_key
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

    def get_segment_loc(self, loc):
        """
        Input is the absolute schedule location and the result is the
        relative segment location along with the Segment object
        :param loc: absolute schedule location
        :return: (Segment, relative_location)
        """
        loc %= self.roundtrip
        distance = 0
        segment = self.segments[0]
        while (distance + segment.trip_length) < loc:
            distance += segment.trip_length
            segment = self.order[segment]
        return segment, loc - distance

    def get_schedule_loc(self, segment, loc):
        """
        Input is the relative segment location and the result is the
        absolute schedule location
        :param segment: Segment object of the current location
        :param loc: relative segment location
        :return: (Segment, relative_location)
        """
        distance = -loc
        while segment != self.segments[0]:
            distance += segment.trip_length
            segment = self.order[segment]
        return (self.roundtrip - distance) % self.roundtrip

    def get_start_locs(self):
        """
        Find all of the driver starting locations; remember location is
        time from the origin and not a physical location
        :return: {start_loc: driver}
        """
        start_locs = {}
        drivers = sorted([driver.id for driver in self.drivers]) # sort driver ids
        last = self.offset  # starting position is equal to the schedule's offset
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
        # Stitch prev and current drivers together
        stitch = stitch_dicts(self.prev.end_locs, start_locs)

        # Check for errors
        # print(self.prev.end_locs, start_locs)
        if stitch == 'Sizes incongruent problem':
            raise IncongruentSchedulesError('Joint route {} has schedules that are incongruent:'.format(self.joint) +
                                            ' {} and {}'.format(self.prev.id, self.id))

        elif stitch == 'Duplicate problem':
            raise MismatchedJointSchedulesTimingError('Joint route {} has schedules with '.format(self.joint) +
                                                      'mismatched timing likely to do significant differences in ' +
                                                      'route design: {} {}'.format(self.prev.id, self.id))

        elif stitch == 'Lax problem':
            raise LaxConstraintFailureError('Joint route {} has schedules that violate the LAX '.format(self.joint) +
                                            'constraint: {} {}'.format(self.prev.id, self.id))

        return stitch

    def generate_trips(self, loc, driver):
        segment, start_loc = self.get_segment_loc(loc)
        end_loc = start_loc
        start = copy.deepcopy(self.start)
        end = copy.deepcopy(self.end)
        while start < end:

            # Calculate end_loc
            # Find the end time which is the start time + Segment.trip_length - start_loc time
            trip_end = start + datetime.timedelta(seconds=(segment.trip_length-start_loc))
            if trip_end > end:
                end_loc = start_loc + (end - start).total_seconds()
            else:
                end_loc = segment.trip_length

            # Set trip
            Trip(self.joint, self, segment, segment.query_stop_seqs(start_loc, end_loc), start_loc, end_loc, start,
                 driver)

            # Calculate next start
            start_loc = 0
            start = trip_end
            segment = self.order[segment] if trip_end < end else segment
            end_loc = 0 if trip_end == end else end_loc

        # Set self.end_locs
        self.end_locs[self.get_schedule_loc(segment, end_loc)] = driver

    def set_trips(self):
        start_locs = self.get_start_locs()

        # Iterate through each driver and set their trips
        for loc in start_locs:
            self.generate_trips(loc, start_locs[loc])

        # Take min loc from origin and add key of loc + roundtrip to create the idea of a circular graph
        self.end_locs[min(self.end_locs) + self.roundtrip] = self.end_locs[min(self.end_locs)]


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
StopTime.publish_matrix()
