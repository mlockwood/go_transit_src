#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

# Python libraries and packages
import datetime

# Import scripts from src
from src.scripts.transit.stop.stop import Stop
from src.scripts.transit.route.direction import Direction
from src.scripts.transit.route.errors import *
from src.scripts.utils.IOutils import load_json, export_json

# Import variables from src
from src.scripts.transit.constants import PATH


class Segment(object):

    objects = {}
    schedule_query = {}
    id_generator = 1

    def __init__(self, joint, schedule_id, dir_order, route, name, direction_id):
        # Initialized attributes
        self.joint = int(joint)
        self.schedule_id = int(schedule_id)
        self.dir_order = int(dir_order)
        self.route = int(route)
        self.name = name
        self.direction = Direction.objects[int(direction_id)]
        self.direction_id = int(direction_id)

        # Attributes set after initialization
        self.trip_generator = 1
        self.trip_length = 0
        self.seq_order = {}  # {StopSeq.order: StopSeq}
        self.stops = {}  # {StopSeq.stop: True}

        # Add to objects
        Segment.objects[(joint, schedule_id, name)] = self
        if schedule_id not in Segment.schedule_query:
            Segment.schedule_query[schedule_id] = {}
        Segment.schedule_query[schedule_id][self] = True

    def __repr__(self):
        return '<Segment {}>'.format(self.name)

    def __str__(self):
        return 'Segment {} for joint {}'.format(self.name, self.joint)

    def __lt__(self, other):
        return (self.joint, self.schedule_id, self.name) < (other.joint, other.schedule_id, other.name)

    def __le__(self, other):
        return (self.joint, self.schedule_id, self.name) <= (other.joint, other.schedule_id, other.name)

    def __eq__(self, other):
        return (self.joint, self.schedule_id, self.name) == (other.joint, other.schedule_id, other.name)

    def __ne__(self, other):
        return (self.joint, self.schedule_id, self.name) != (other.joint, other.schedule_id, other.name)

    def __gt__(self, other):
        return (self.joint, self.schedule_id, self.name) > (other.joint, other.schedule_id, other.name)

    def __ge__(self, other):
        return (self.joint, self.schedule_id, self.name) >= (other.joint, other.schedule_id, other.name)

    def __hash__(self):
        return hash((self.joint, self.schedule_id, self.name))

    @staticmethod
    def set_segments():
        for obj in Segment.objects:
            segment = Segment.objects[obj]

            # If Segment name not in StopSeq.segment_query alert planner that the sheet has no identified StopSeqs
            if segment.name not in StopSeq.segment_query:
                raise SegmentNameDoesNotHaveStopSeqs('Segment {} has no StopSeqs.'.format(segment.name))

            # Examine and extract all StopSeqs related to Segment name
            for stop_seq in StopSeq.segment_query[segment.name]:

                # Verify that a duplicate arrival is not present
                if stop_seq.arrive in segment.seq_order:
                    raise DuplicateTimingSpreadError('{} duplicate arrival time of {}'.format(segment.name,
                                                                                              stop_seq.arrive))

                # Add order[arrival] = i
                segment.seq_order[stop_seq.arrive] = stop_seq

                # If the destination is true, set current StopSeq's depart as the trip_length for the segment
                if stop_seq.destination:
                    segment.trip_length = stop_seq.depart

                # Add the StopSeq stop to segment.stops
                segment.stops[stop_seq.stop] = True

            segment.set_order()

    @classmethod
    def load(cls):
        Direction.load()
        load_json('{}/data/segment.json'.format(PATH), cls)

    @classmethod
    def export(cls):
        export_json('{}/data/segment.json'.format(PATH), cls)

    def get_json(self):
        return dict([(k, getattr(self, k)) for k in ['joint', 'schedule_id', 'dir_order', 'route', 'name',
                                                     'direction_id']])

    def set_order(self):
        # List of stop_ids in order of travel_time
        temp = [self.seq_order[key] for key in sorted(self.seq_order.keys())]

        # Convert temp list to dictionary of segment order
        order = {}
        i = 0
        for stop_seq in temp:
            order[i] = stop_seq  # set self.order[StopSeq.order] = StopSeq object
            stop_seq.order = i  # transfer order to StopSeq objects
            i += 1
        self.seq_order = order
        return True

    def query_stop_seqs(self, start_loc, end_loc):
        """
        Select all StopSeqs that occur between the start_loc and
        end_loc times. NotImplemented: Binary Tree version.
        :param start_loc: time location for when the trip started
        :param end_loc: time locations for when the trip ended
        :return: {StopSeq: True}
        """
        query = {}
        for key in self.seq_order.keys():
            if start_loc <= self.seq_order[key].depart and self.seq_order[key].arrive <= end_loc:
                query[self.seq_order[key]] = True
        return query

    def query_min_stop_seq(self, start_loc, end_loc):
        """
        Select the minimum StopSeq between the start_loc and
        end_loc times if there are StopSeqs that qualify.
        :param start_loc: time location for when the trip started
        :param end_loc: time locations for when the trip ended
        :return: stop_id
        """
        for key in sorted(self.seq_order.keys()):
            if start_loc <= self.seq_order[key].depart and self.seq_order[key].arrive <= end_loc:
                return self.seq_order[key].stop
        return None


class StopSeq(object):

    objects = {}
    segment_query = {}

    def __init__(self, segment, stop, arrive, depart, timed, display, load_seq, destination):
        # Stop validation
        if stop not in Stop.objects:
            raise UnknownStopPointError('Stop {} from {} is not recognized.'.format(stop, segment))

        # Assign attributes
        self.segment = segment
        self.stop = stop
        self.arrive = int(arrive)
        self.depart = int(depart)
        self.gtfs_depart = int(arrive) if destination else int(depart)
        self.timedelta = datetime.timedelta(seconds=(self.depart - self.arrive))
        self.gtfs_timedelta = datetime.timedelta(seconds=(self.gtfs_depart - self.arrive))
        self.timed = int(timed)
        self.display = int(display)
        self.load_seq = int(load_seq)
        self.destination = destination
        self.order = None

        StopSeq.objects[(segment, load_seq)] = self
        if segment not in StopSeq.segment_query:
            StopSeq.segment_query[segment] = {}
        StopSeq.segment_query[segment][self] = True

    @classmethod
    def load(cls):
        load_json(PATH + '/data/stop_seq.json', cls)
        Segment.set_segments()

    @classmethod
    def export(cls):
        export_json(PATH + '/data/stop_seq.json', cls)

    def get_json(self):
        return dict([(k, getattr(self, k)) for k in ['segment', 'stop', 'arrive', 'depart', 'timed', 'display',
                                                     'load_seq', 'destination']])
