#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

# Python libraries and packages
import datetime

# Import scripts from src
from src.scripts.utils.classes import DataModelTemplate
from src.scripts.route.errors import *

# Import variables from src
from src.scripts.constants import *


class Segment(DataModelTemplate):

    id_generator = 1
    json_path = '{}/route/segment.json'.format(DATA_PATH)
    objects = {}
    schedule_query = {}

    def set_object_attrs(self):
        self.dir_type_num = 0
        self.trip_generator = 1
        self.trip_length = 0
        self.seq_order = {}  # {StopSeq.order: StopSeq}; ex {1: '100a'}
        self.stops = {}  # {StopSeq.stop: True}; ex {'100a': True}
        self.locs = {}  # {StopSeq.stop[:3]: [<StopSeq>, ...]}; ex {'100': [<StopSeq 100a>, <StopSeq 100b>]}

    def __repr__(self):
        return '<Segment {}>'.format(self.name)

    def __str__(self):
        return 'Segment {} for route {}'.format(self.name, self.route)

    def __lt__(self, other):
        return self.id < other.id

    def __le__(self, other):
        return self.id <= other.id

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        return self.id != other.id

    def __gt__(self, other):
        return self.id > other.id

    def __ge__(self, other):
        return self.id >= other.id

    def __hash__(self):
        return hash(self.id)

    def get_json(self):
        attrs = dict([(k, getattr(self, k)) for k in ['description', 'direction', 'id', 'route']])
        return attrs

    def set_segment(self):
        # Alert the planner if the sheet has no identified StopSeqs
        if not self.stops:
            raise SegmentNameDoesNotHaveStopSeqs('Segment {} has no StopSeqs.'.format(self.id))

        # Set order for the segment; start with a list of stop_ids in order of travel_time
        temp = [self.seq_order[key] for key in sorted(self.seq_order.keys())]

        # Convert temp list to dictionary of segment order
        order = {}
        i = 0
        for stop_seq in temp:
            order[i] = stop_seq  # set self.order[StopSeq.order] = StopSeq object
            stop_seq.order = i  # transfer order to StopSeq objects
            i += 1
        self.seq_order = order

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


class StopSeq(DataModelTemplate):

    json_path = '{}/route/stop_seq.json'.format(DATA_PATH)
    objects = {}

    def set_object_attrs(self):
        self.gtfs_depart = self.arrive if self.destination else self.depart
        self.timedelta = datetime.timedelta(seconds=(self.depart - self.arrive))
        self.gtfs_timedelta = datetime.timedelta(seconds=(self.gtfs_depart - self.arrive))
        self.order = None
        self.add_to_segment()

    def set_objects(self):
        StopSeq.objects[(self.segment, self.load_seq)] = self

    def get_json(self):
        return dict([(k, getattr(self, k)) for k in ['segment', 'stop', 'arrive', 'depart', 'timed', 'display',
                                                     'load_seq', 'destination']])

    def add_to_segment(self):
        self.segment = Segment.objects[self.segment]

        # Verify that a duplicate arrival is not present
        if self.arrive in self.segment.seq_order:
            raise DuplicateTimingSpreadError('{} duplicate arrival time of {}'.format(self.segment.name, self.arrive))

        # Add order[arrival] = i
        self.segment.seq_order[self.arrive] = self

        # If the destination is true, set current StopSeq's depart as the trip_length for the segment
        if self.destination:
            self.segment.trip_length = self.depart

        # Add the StopSeq stop to self.stops and StopSeq loc to self.locs
        self.segment.stops[self.stop] = True
        if self.stop[:3] not in self.locs:
            self.locs[self.stop[:3]] = []
        self.locs[self.stop[:3]] = self.locs.get(self.stop[:3]) + [self]


def load():
    Segment.load()
    StopSeq.load()
    for obj in Segment.objects:
        Segment.objects[obj].set_segment()
