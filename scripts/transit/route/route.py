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
from src.scripts.transit.route.errors import *

# Classes and variables from src
from src.scripts.transit.constants import PATH
from src.scripts.transit.route.constants import DATE, STOP_TIME_HEADER
from src.scripts.utils.IOutils import load_json, export_json

from src.scripts.transit.route.segment import Segment, StopSeq
from src.scripts.transit.route.service import Service
from src.scripts.transit.route.trip import Trip, StopTime

# Import classes and functions from src
from src.scripts.utils.functions import stitch_dicts

# Import variables from src
from src.scripts.transit.route.constants import LAX


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
                                            self.route.trip_id, self.segment)

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
        self.segments = {}  # {'0700-0745': {0: <Segment>, 1: <Segment>, ... } ... }  RENAME TO AVOID RG CONFUSION
        """
        self.route_graphs = {}  # {time: RouteGraph}
        """
        Joint.objects[int(id)] = self

    @classmethod
    def load(cls):
        load_json('{}/data/routes/joint.json'.format(PATH), cls)

    @classmethod
    def export(cls):
        export_json('{}/data/routes/joint.json'.format(PATH), cls)

    def get_json(self):
        return dict([(k, getattr(self, k)) for k in ['id', 'desc', 'routes', 'service_id', 'headway']])

    @staticmethod
    def process(date):
        # Set up self.segments

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
                            StopTime.objects[(trip.id, seq)].joint = joint.id

        return True


class RouteGraph(object):

    objects = {}

    def __init__(self, joint, time, segments, prev=None):
        # Initialized attributes
        self.joint = joint
        self.time = time
        self.segments = segments  # {0: <Segment>, 1: <Segment>, 2: <Segment> ... }

        # Attributes set after initialization
        self.headway = joint.headway  # PERHAPS REFACTOR THIS TO CALL FROM self.joint?----------------------------------
        self.roundtrip = 0

        # Set attributes
        self.prev = self.check_prev(prev)
        self.drivers = Driver.get_drivers(math.ceil(self.roundtrip / self.headway)) if not prev else prev.drivers
        self.order = self.get_order()

        # Make schedules
        self.schedules = {}
        self.hidden_key = {}
        self.set_schedules()

        # Add to objects
        RouteGraph.objects[(joint, time)] = self

    def check_prev(self, prev):
        if prev:
            # If the number of driver shifts between this and the previous schedule do not match
            if len(prev.drivers) != math.ceil(self.roundtrip / self.headway):
                # Raise an error because they should match
                raise JointRouteMismatchedDriverCount('JointRoute {} has mismatched driver counts for {} and {}'.format(
                    self.joint.id, self.prev.time, self.time))

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

    def get_trip_length(self, a, b, order):
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
            a = a.segment.id

        # If the destination is a StopSeq add the departure time to the trip_length
        if re.search('stopseq', str(b.__class__).lower()):
            trip_length += b.depart
            b = b.segment.id

        # Continue traveling the order until the cur_segment and final_segment are the same
        while a != b:
            # Add current segment's trip length to the prev_trip_length
            trip_length += Segment.objects[order[a]].trip_length
            # Shift the cur_segment forward
            a = order[a]

        return trip_length if trip_length != self.roundtrip else 0

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

    def get_trip_starts(self):
        # Set ordered drivers
        drivers = sorted([driver.id for driver in self.drivers])

        adjustment = (self.headway - self.segments[0].offset) % self.headway
        origin_time = self.segments[0].sheet.start - (datetime.timedelta(seconds=adjustment))

        try:
            trip_starts = [(drivers[0], self.segments[0].trips[origin_time], origin_time)]

        except KeyError:
                trip, origin_time = self.trip_start_helper(origin_time, self.trips[0][0])
                trip_starts = [(drivers[0], trip, origin_time)]

        mid_trip_distance = (self.headway - self.segments[0].offset) % self.headway
        cur_segment = self.trips[0][0]  # IS self.trips[0][0] == self.segments[0]?--------------------------------------

        for driver in drivers[1:]:
            mid_trip_distance += self.headway

            # Continue to rotate segments and reduce the length mid_trip if mid_trip >= current segment trip length
            while mid_trip_distance >= Segment.objects[cur_segment].trip_length:
                mid_trip_distance -= Segment.objects[cur_segment].trip_length
                cur_segment = self.order[cur_segment]

            # Add final mid_trip_distance to the trip_starts list
            origin_time = Segment.objects[cur_segment].start - datetime.timedelta(seconds=mid_trip_distance)

            # Try to add as-is, but if a key error then progress. See documentation #X ---------------------------------
            try:
                trip_starts += [(driver, Segment.objects[cur_segment].trips[origin_time], origin_time)]

            except KeyError:
                trip, origin_time = self.trip_start_helper(origin_time, cur_segment)
                trip_starts += [(driver, trip, origin_time)]

        return trip_starts

    def stitch_prev(self, starting):
        # Collect trip_origins from previous schedule
        a = []
        for driver in self.prev.schedules:
            a.append(self.prev.schedules[driver][max(self.prev.schedules[driver])])
        a = self.get_time_locations(self.prev.trips[0][0], a, self.prev.order, minimum=False)
        # Add in the minimum trip at the other end to create the idea of a circular list/graph
        a[min(a) + self.roundtrip] = a[min(a)]

        # Collect trip_origins from current starts
        b = []
        for position in starting:
            b.append(position[1])
        b = self.get_time_locations(self.trips[0][0], b, self.order)

        # Stitch A and B trips together
        stitch = stitch_dicts(a, b)

        # Check for errors
        if stitch == 'Sizes incongruent problem':
            raise IncongruentSchedulesError('Joint route {} has schedules that are incongruent:'.format(self.joint) +
                                            ' {} and {}'.format(self.prev.service.id, self.service.id))

        elif stitch == 'Duplicate problem':
            raise MismatchedJointSchedulesTimingError('Joint route {} has schedules with '.format(self.joint) +
                                                      'mismatched timing likely to do significant differences in ' +
                                                      'route design: {} {}'.format(self.prev.service.id,
                                                                                   self.service.id))

        elif stitch == 'Lax problem':
            raise LaxConstraintFailureError('Joint route {} has schedules that violate the LAX '.format(self.joint) +
                                            'constraint: {} {}'.format(self.prev.service.id, self.service.id))

        # Assign drivers from A to B
        new_start = []
        for position in starting:
            # Set the position's driver to the prev driver
            new_start += [(stitch[position[1]].driver, position[1], position[2])]

        return new_start

    def set_schedules(self):
        trip_starts = self.get_trip_starts()

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


JointRoute.load()
# JointRoute.export()