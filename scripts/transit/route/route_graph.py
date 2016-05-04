#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

# Python libraries and packages
import copy
import csv
import datetime
import math
import os
import re

# Import scripts from src
import src.scripts.transit.stop.stop as st
import src.scripts.transit.route.errors as RouteErrors

# Import classes and functions from src
from src.scripts.utils.functions import stitch_dicts

# Import variables from src
from src.scripts.transit.route.constants import LAX


class StopSeq(object):

    def __init__(self, sheet, stop, gps_ref, arrive, depart, timed, display, load_seq, segment):
        # Attributes from sheet
        self.sheet = sheet
        self.stop = stop
        self.gps_ref = gps_ref
        self.arrive = int(re.sub('a', '', arrive))
        self.depart = int(re.sub('d', '', depart))
        self.gtfs_depart = int(re.sub('a', '', arrive)) if re.search('d', depart) else int(depart)
        self.timedelta = datetime.timedelta(seconds=(self.depart - self.arrive))
        self.gtfs_timedelta = datetime.timedelta(seconds=(self.gtfs_depart - self.arrive))
        self.timed = timed
        self.display = display
        self.load_seq = load_seq
        self.segment = segment

        # Attributes from processing
        self.order = None
        self.stop_times = {}


class Segment(object):

    objects = {}
    id_generator = 1

    def __init__(self, route, sheet):
        # Initialized attributes
        self.route = route
        self.sheet = sheet
        self.id = hex(Segment.id_generator)
        Segment.id_generator += 1

        # Attributes obtained from sheet
        self.dirnum = sheet.dirnum
        self.direction = sheet.direction
        self.offset = sheet.offset
        self.headway = sheet.headway
        self.service = sheet.service
        self.start = sheet.start
        self.end = sheet.end

        # Attributes set after initialization
        self.origin = (0, 'a')
        self.destination = (0, 'a')
        self.trip_length = 0
        self.stop_seqs = {}
        self.order = {}
        self.trips = {}
        self.trip = []

        # Add to objects
        Segment.objects[self.id] = self

    def __repr__(self):
        return '<Segment from {} for direction {}>'.format(self.sheet.sheet, self.direction.id)

    def add_stop_seq(self, stop_seq):
        # Ensure the stop_seq object is added to self.stop_seqs
        self.stop_seqs[stop_seq] = True

        # Verify that a duplicate arrival is not present
        if stop_seq.arrive in self.order:
            raise RouteErrors.DuplicateTimingSpreadError('Sheet {} has a duplicate arrival '.format(self.sheet) +
                                                         'value of {}'.format(stop_seq.arrive))

        # Add order[arrival] = i
        self.order[stop_seq.arrive] = stop_seq.load_seq
        return True

    def set_order(self):
        # List of stop_ids in order of travel_time
        temp = [self.order[key] for key in sorted(self.order.keys())]

        # Convert temp list to dictionary of segment order
        order = {}
        i = 1
        for row_id in temp:
            order[row_id] = i
            i += 1
        self.order = order

        # Transfer order to stop_seq objects and set their stop_times
        for stop_seq in self.stop_seqs:
            stop_seq.order = self.order[stop_seq.load_seq]

        # Convert stop_seqs to stop_seqs[stop_seq] = StopSeq
        temp = {}
        for stop_seq in self.stop_seqs:
            temp[stop_seq.order] = stop_seq
        self.stop_seqs = temp

        return True

    def set_trip(self):
        self.trip = [self.id, self.origin[0], self.destination[0]]  # SHOULD GPS REF BE INCLUDED BY DROPPING THE INDEX?
        return True


class RouteGraph(object):

    objects = {}

    def __init__(self, joint, service, segments, prev=None):
        # Initialized attributes
        self.joint = joint
        self.service = service
        self.segments = segments

        # Attributes set after initialization
        self.headway = 0
        self.roundtrip = 0

        # Set attributes
        self.prev = self.check_prev(prev)
        self.drivers = Driver.get_drivers(self.get_drivers()) if not prev else prev.drivers
        self.trips = self.set_trips()

        # Create a dictionary for all trips
        unset = dict((tuple(x), True) for x in self.trips)
        # Delete the first trip which is taken before the order is set
        del unset[tuple(self.trips[0])]
        # Call order function
        if len(self.trips) > 1:
            self.order = self.set_order(self.trips[0][0], self.trips[0][2], {}, copy.deepcopy(unset))
        else:
            self.order = {self.trips[0][0]: self.trips[0][0]}

        # Make schedules
        self.schedules = {}
        self.hidden_key = {}
        self.set_schedules()

        # Add to objects
        RouteGraph.objects[(joint, service.id)] = self

    def check_prev(self, prev):
        if prev:
            # If the number of driver shifts between this and the previous schedule do not match...
            if len(prev.drivers) != self.get_drivers():
                # ...set prev to None
                prev = None

        return prev

    def get_drivers(self):
        # Find joint roundtrip
        for segment in self.segments:
            # If the headway for the RouteGraph has not been set, set it equal to the first Segment
            if not self.headway:
                self.headway = segment.headway

            # Verify that all segments have the same headway
            if segment.headway != self.headway:
                raise RouteErrors.JointHeadwayNotMatchError('The headways for joint key {}.'.format(self.joint) +
                                                            ' and schedule {} do not match.'.format(self.service))
            self.roundtrip += segment.trip_length

        # Find the number of drivers based on the roundtrip and headway
        n = math.ceil(self.roundtrip / self.headway)

        # Convert driver number to range of drivers
        return n

    def set_trips(self):
        trips = []
        for segment in self.segments:
            segment.set_trip()
            trips.append(segment.trip)
        return trips

    def set_order(self, key, nxt, order, unset):
        """
        The set_order is a recursive function that attempts to link
        trips for the JointRoute object. Note that these trips are not
        the same as the Trip class in Route.py. There is only one trip
        for each direction instead of a trip for each headway in each
        direction. The final order will have the representation of
        {segment_id: next_segment_id}
        :param key: The Segment object representing the trip
        :param nxt: The previous destination and origin of next trip.
        :param order: The dict() of currently set ordered trips
        :param unset: The dict() of trips that have not yet been set.
        :return: True when executed properly, exceptions may be raised.
        """
        # Base case - no more trips need to be set
        if not unset:
            if nxt != self.trips[0][1]:
                raise RouteErrors.JointRoutesNotMatchError('Trips from joint key {} do not have '.format(self.joint) +
                                                           'matching origin and destination values.')
            order[key] = self.trips[0][0]
            return order

        # Find acceptable trips
        for option in unset:
            if option[1] == nxt:
                # Set new values
                new_key = option[0]
                new_nxt = option[2]

                # Deepcopy the order and add current trip
                new_order = copy.deepcopy(order)
                new_order[key] = new_key

                # Deepcopy unset and del current trip
                new_unset = copy.deepcopy(unset)
                del new_unset[option]

                # Recurse with updated order
                return self.set_order(new_key, new_nxt, new_order, new_unset)

        # If no trips were deemed acceptable
        raise RouteErrors.JointRoutesNotMatchError('Trips from joint key {} do not have '.format(self.joint) +
                                                   'matching origin and destination values.')

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

    def get_trip_origins(self, origin, trips, order, minimum=True):
        trip_origins = {}
        for trip in trips:

            # Add the prev_trip_length time for connected segments after the origin before this trip if applicable
            # Then set the result as the key for the travel time since the origin for the start of the trip
            if minimum:
                trip_origins[self.get_trip_length(origin, trip.segment.stop_seqs[min(trip.stop_times)], order)] = trip
            else:
                trip_origins[self.get_trip_length(origin, trip.segment.stop_seqs[max(trip.stop_times)], order)] = trip

        return trip_origins

    def get_trip_order(self, trips, order):
        trip_origins = self.get_trip_origins(self.trips[0][0], trips, order)
        # Convert dict to list ordered by key of arrival time but value set to trip
        trip_order = []
        for key in sorted(trip_origins.keys()):
            trip_order.append(trip_origins[key])
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
        a = self.get_trip_origins(self.prev.trips[0][0], a, self.prev.order, minimum=False)
        # Add in the minimum trip at the other end to create the idea of a circular list/graph
        a[min(a) + self.roundtrip] = a[min(a)]

        # Collect trip_origins from current starts
        b = []
        for position in starting:
            b.append(position[1])
        b = self.get_trip_origins(self.trips[0][0], b, self.order)

        # Stitch A and B trips together
        stitch = stitch_dicts(a, b)

        # Check for errors
        if stitch == 'Sizes incongruent problem':
            raise RouteErrors.IncongruentSchedulesError('Joint route {} has schedules that are '.format(self.joint) +
                                                        'incongruent: {} and {}'.format(self.prev.service.id,
                                                                                        self.service.id))
        elif stitch == 'Duplicate problem':
            raise RouteErrors.MismatchedJointSchedulesTimingError('Joint route {} has schedules '.format(self.joint) +
                                                                  'with mismatched timing likely to do significant ' +
                                                                  'differences in route design: {} {}'.format(
                                                                      self.prev.service.id,
                                                                      self.service.id))

        elif stitch == 'Lax problem':
            raise RouteErrors.LaxConstraintFailureError('Joint route {} has schedules that '.format(self.joint) +
                                                        'violate the LAX constraint: {} {}'.format(self.prev.service.id,
                                                                                                   self.service.id))

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
            starting = self.stitch_prev(trip_starts)

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

