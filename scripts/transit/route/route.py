#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

# Python libraries and packages
import copy
import datetime
import math
import re
import uuid

# Entire scripts from src
from src.scripts.transit.stop.stop import Stop
from src.scripts.transit.route.errors import *

# Classes and variables from src
from src.scripts.constants import *
from src.scripts.utils.classes import DataModelTemplate

from src.scripts.transit.route.segment import Segment, StopSeq, Direction
from src.scripts.transit.route.service import Service
from src.scripts.transit.route.trip import Trip, StopTime

# Import classes and functions from src
from src.scripts.utils.functions import stitch_dicts

# Load dependent data
Stop.load()
Direction.load()
Segment.load()
StopSeq.load()
Segment.set_segments()
Service.load()


class Route:

    route_query = {}

    @staticmethod
    def set_route_query():
        for obj in Schedule.objects:
            schedule = Schedule.objects[obj]

            for dir_order in schedule.segments:
                segment = schedule.segments[dir_order]

                if segment.route not in Route.route_query:
                    Route.route_query[segment.route] = {}

                start = schedule.joint.service.start_date
                end = schedule.joint.service.end_date

                if (start, end) not in Route.route_query[segment.route]:
                    Route.route_query[segment.route][(start, end)] = {}

                for stop in segment.stops:
                    # It is important to remove the GPS_REF
                    Route.route_query[segment.route][(start, end)][stop[:3]] = True

        return True

    @staticmethod
    def query_route(route, date, stop):
        if route in Route.route_query:
            for key in Route.route_query[route]:
                if key[0] <= date <= key[1]:
                    if stop in Route.route_query[route][key]:
                        return True
        return False


class Joint(DataModelTemplate):

    objects = {}
    json_path = '{}/joint.json'.format(DATA_PATH)
    locations = {}

    def set_object_attrs(self):
        self.service = Service.objects[self.service]
        self.schedules = {}

    def __repr__(self):
        return '<Joint {}>'.format(self.id)

    @staticmethod
    def process():
        ranges = {}
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

            date_key = (joint.service.start_date, joint.service.end_date + datetime.timedelta(days=1))
            if date_key not in ranges:
                ranges[date_key] = []
            ranges[date_key] = ranges.get(date_key) + [joint]

        DateRange.set_ranges(ranges)
        return True

    def get_json(self):
        attrs = dict([(k, getattr(self, k)) for k in ['id', 'desc', 'routes', 'headway']])
        attrs['service'] = self.service.id
        return attrs


class Schedule(DataModelTemplate):

    objects = {}
    json_path = '{}/schedule.json'.format(DATA_PATH)

    def set_object_attrs(self):
        self.joint = Joint.objects[self.joint]
        self.start_str = self.start
        self.end_str = self.end

        # Set times
        self.start = copy.deepcopy(self.joint.service.start_date).replace(hour=int(self.start[:2]),
                                                                          minute=int(self.start[-2:]))
        self.end = copy.deepcopy(self.joint.service.start_date).replace(hour=int(self.end[:2]),
                                                                        minute=int(self.end[-2:]))
        # Handle end times that are at or after midnight (24+ hour scale for GTFS) by incrementing the day
        if self.end < self.start:
            self.end = self.end + datetime.timedelta(days=1)

        if 'drivers' not in self.__dict__:
            self.drivers = {}

        self.prev = None
        self.segments = self.get_segments()
        self.roundtrip = self.get_roundtrip()
        self.order = self.get_order()
        self.joint.schedules[self] = True
        self.end_locs = {}

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

    def get_json(self):
        return {
            'id': self.id,
            'offset': self.offset,
            'joint': self.joint.id,
            'start': self.start_str,
            'end': self.end_str,
            'drivers': dict((driver, self.drivers[driver].id) for driver in self.drivers)
        }

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
        DEPRECATED but still a potentially useful function
        :param a: The origin of the trip; MUST be a Segment id OR a
            StopSeq object
        :param b: The destination of the trip; MUST be a Segment id OR a
            StopSeq object
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
        last = self.offset  # starting position is equal to the schedule's offset
        d = 0  # index of the current driver position

        while d < len(self.drivers):
            start_locs[last] = self.drivers[d]
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
            trip = Trip(**{
                'id': '-'.join(str(s) for s in [self.joint.id, self.id, segment.name, segment.trip_generator]),
                'schedule': self.id,
                'direction': segment.direction.id,
                'start_loc': start_loc,
                'end_loc': end_loc,
                'start_time': start.strftime('%Y%m%d-%H%M%S'),
                'driver': driver
            })
            segment.trip_generator += 1
            trip.create_stop_times(segment.query_stop_seqs(start_loc, end_loc), self.joint.service)

            # Set driver start location
            driver.start = segment.query_min_stop_seq(start_loc, end_loc)

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


class DateRange(DataModelTemplate):

    json_path = '{}/date_range.json'.format(DATA_PATH)
    objects = {}

    def set_object_attrs(self):
        self.start = datetime.datetime.strptime(self.start, '%Y-%m-%d')
        self.end = datetime.datetime.strptime(self.end, '%Y-%m-%d')
        self.joints = [Joint.objects[joint] for joint in self.joints]

    def set_objects(self):
        DateRange.objects[(self.start, self.end)] = self

    def __repr__(self):
        return '<DateRange {}-{}>'.format(self.start, self.end)

    @staticmethod
    def set_ranges(ranges):
        """
        Build non-overlapping DateRange objects populated with all
        joint routes within the DateRange object's start and end date.
        :param ranges: {(start, end): [Joint, Joint, ... ]}
        :return: True after setting up DateRange objects with joints
        """
        # Find all unique start and end dates
        points = {}
        for date_range in ranges:
            for date in date_range:
                points[date] = True
        points = sorted(list(points.keys()))

        # Order the dates and create ranges between each two ordered points
        i = 0
        while i < len(points) - 1:
            DateRange(**{
                'start': points[i].strftime('%Y-%m-%d'),
                'end': points[i+1].strftime('%Y-%m-%d'),
                'joints': []
            })
            i += 1

        # Connect Joint objects to DateRange objects
        for date_range in ranges:
            for obj in DateRange.objects:
                if date_range[0] <= DateRange.objects[obj].start and date_range[1] >= DateRange.objects[obj].end:
                    DateRange.objects[obj].joints += ranges[date_range]

    @staticmethod
    def get_feed_by_date(date):
        trips = None
        for obj in DateRange.objects:
            date_range = DateRange.objects[obj]
            if date_range.start <= date < date_range.end:
                trips = date_range.get_feed()
        return trips

    def get_feed(self):
        trips = {}
        stop_times = {}

        self.joints = [Joint.objects[joint] for joint in sorted([joint.id for joint in self.joints])]

        # Set driver positions and collect trips
        position = 1
        for joint in self.joints:
            for schedule in joint.schedules:
                for driver in sorted(schedule.drivers.keys()):
                    # Set the driver's position if schedule has not been seen
                    if not schedule.prev:
                        schedule.drivers[driver].position = position
                        position += 1

                # Select trips
                trips.update(Trip.feed[schedule.id])

                # Select stop_times
                stop_times.update(StopTime.feed[schedule.id])

        return trips, stop_times

    def get_json(self):
        return {
            'joints': [joint.id for joint in self.joints],
            'start': self.start.strftime('%Y-%m-%d'),
            'end': self.end.strftime('%Y-%m-%d')
        }


class Driver(DataModelTemplate):

    json_path = '{}/route_driver.json'.format(DATA_PATH)
    objects = {}

    @classmethod
    def get_drivers(cls, n):
        return dict([(x, cls(**{
            'id': str(uuid.uuid4()),
            'start': None,
            'position': None
        })) for x in range(n)])

    @classmethod
    def reconstruct_object_links(cls):
        for obj in Schedule.objects:
            sch = Schedule.objects[obj]
            sch.drivers = dict((driver, Driver.objects[sch.drivers[driver]]) for driver in sch.drivers)
        for obj in Trip.objects:
            Trip.objects[obj].driver = Driver.objects[Trip.objects[obj].driver]
        return True


def process():
    Joint.load()
    Schedule.load()
    Joint.process()
    Route.set_route_query()
    feed = DateRange.get_feed_by_date(datetime.datetime.today())
    StopTime.publish_matrix()
    Schedule.export()
    DateRange.export()
    Driver.export()
    Trip.export()
    StopTime.export()
    return feed


def load():
    Joint.load()
    Schedule.load()
    DateRange.load()
    Driver.load()
    Trip.load()
    StopTime.load()
    Driver.reconstruct_object_links()
    feed = DateRange.get_feed_by_date(datetime.datetime.today())
    StopTime.publish_matrix()
    return feed

if __name__ == "__main__":
    # feed = process()
    feed = load()
    print(len(feed[0]), len(feed[1]))
