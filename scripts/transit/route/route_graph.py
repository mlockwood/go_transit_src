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
from src.scripts.transit.route.constants import DATE


class StopSeq(object):

    def __init__(self, sheet, stop, gps_ref, arrive, depart, timed, display, stop_seq):
        # Attributes from sheet
        self.sheet = sheet
        self.stop = stop
        self.gps_ref = gps_ref
        self.arrive = int(re.sub('a', '', arrive))
        self.depart = int(re.sub('d', '', depart))
        self.timedelta = datetime.timedelta(seconds=(self.depart - self.arrive))
        self.timed = timed
        self.display = display
        self.stop_seq = stop_seq

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
        self.start = sheet.start
        self.end = sheet.end

        # Attributes set after initialization
        self.origin = (0, 'a')
        self.destination = (0, 'a')
        self.trip_length = 0
        self.stop_seqs = {}
        self.order = {}
        self.origin_times = {}
        self.start_trips = []
        self.trip = []

        # Add to objects
        Segment.objects[id] = self

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
        self.prev = prev

        # Attributes set after initialization
        self.headway = 0
        self.roundtrip = 0

        # Set attributes
        self.drivers = self.set_drivers()
        self.trips = self.set_trips()

        # Create a dictionary for all trips
        unset = dict((tuple(x), True) for x in self.trips)
        # Delete the first trip which is taken before the order is set
        del unset[tuple(self.trips[0])]

        # Call order function
        self.order = self.set_order(self.trips[0][0], self.trips[0][2], {}, copy.deepcopy(unset))
        self.back_order = self.set_back_order()

        # Find first driving start position and then build schedules
        self.anchors = self.set_anchors()
        self.schedules = {}
        self.hidden_key = {}
        self.locations = {}
        self.set_schedules()

        # Add to objects
        RouteGraph.objects[(joint, service.id)] = self

    def set_drivers(self):
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
        return Driver.get_drivers(n)

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

    def set_back_order(self):
        back_order = {}
        for key in self.order:
            back_order[self.order[key]] = key
        return back_order

    def get_prev_trip_length(self, cur_segment, final_segment):
        prev_trip_length = 0

        # Continue traveling the order until the cur_segment and final_segment are the same
        while cur_segment != final_segment:
            # Add current segment's trip length to the prev_trip_length
            prev_trip_length += self.order[cur_segment]
            # Shift the cur_segment forward
            cur_segment = self.order[cur_segment]

        return prev_trip_length

    def set_anchors(self):
        anchors = {}
        for segment in self.segments:
            for trip in segment.start_trips:
                anchors[trip] = True
        return anchors

    def get_trip_order(self):
        trip_order = {}
        for trip in self.anchors:
            # Find the arrival time for the first stop_time via the Trip's Segment's StopSeq for the stop_time
            spread = trip.segment.order[min(trip.stop_times.keys())].arrive

            # Add the prev_trip_length time for connected segments after the origin before this trip if applicable
            # Then set the result as the key for the travel time since the origin for the start of the trip
            trip_order[spread + self.get_prev_trip_length(self.trips[0][0], trip.segment.id)] = trip

        # Convert dict to list ordered by key of arrival time but value set to trip
        new_order = []
        for key in sorted(trip_order.keys()):
            new_order.append(trip_order[key])
        return trip_order

    def set_schedules(self):
        # Set a driver, in order, for each starting position
        trip_order = self.get_trip_order()
        driver_ids = sorted([driver.id for driver in self.drivers])
        starting = [x for x in zip(driver_ids, trip_order)]

        # Initialize schedule for each driver
        for position in starting:
            time = self.service.start_time - datetime.timedelta(seconds=position[1].segment.trip_length)
            self.schedules[position[0]] = {[position[1]]: time}
            self.hidden_key[position[0]] = (position[1].segment.id, time)

        # Forward path
        for driver in self.schedules:
            order = self.hidden_key[driver][0]  # order should always be a Segment id
            time = self.hidden_key[driver][1]
            while True:

                # Find the time to reach the next segment from the current segment
                time = time + datetime.timedelta(seconds=Segment.objects[order].trip_length)  # * 60 or no?
                if time > order.end:
                    break

                # Find the next segment from the current segment
                order = self.order[order]

                # Convert time to trip id from next segment
                # self.schedules[driver][trip_id] = time
                self.schedules[driver][Segment.objects[order].origin_time[time]] = time

        # Backward path -- POSSIBLE REDUNDANCY/DEPRECATION
        for driver in self.schedules:
            order = self.trips[0][0]
            time = self.schedules[driver][self.hidden_key[driver]]
            while True:

                # Find the time to reach the previous segment from the current segment
                time = time - datetime.timedelta(0, 60 * Segment.objects[order].trip_length)

                # Find the next segment from the current segment
                order = self.back_order[order]

                try:
                    # Reset hidden key to be able to determine start values
                    self.hidden_key[driver] = Segment.objects[order].origin_time[time]

                    # Convert time to trip id
                    self.schedules[driver][Segment.objects[order].origin_time[time]] = time
                except KeyError:
                    break


class Driver:

    objects = {}
    id_generator = 0x1

    def __init__(self):
        self.id = Driver.id_generator
        Driver.id_generator += 1
        Driver.objects[self.id] = self

    @staticmethod
    def get_drivers(n):
        return [Driver() for driver in range(n)]

