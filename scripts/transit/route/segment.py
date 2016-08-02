#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

# Python libraries and packages
import datetime

# Import scripts from src
from src.scripts.utils.classes import DataModelTemplate
from src.scripts.transit.route.direction import Direction
from src.scripts.transit.route.errors import *

# Import variables from src
from src.scripts.constants import PATH


Direction.load()


class Segment(DataModelTemplate):

    id_generator = 1
    json_path = '{}/data/segment.json'.format(PATH)
    objects = {}
    schedule_query = {}

    def set_object_attrs(self):
        self.dir_type_num = 1 if self.dir_type == 'inbound' else 0
        self.direction = Direction.objects[self.direction]
        self.trip_generator = 1
        self.trip_length = 0
        self.seq_order = {}  # {StopSeq.order: StopSeq}
        self.stops = {}  # {StopSeq.stop: True}
        self.locs = {}  # {StopSeq.stop[:3]: [<StopSeq>, <StopSeq>, ...]}

        if self.schedule not in Segment.schedule_query:
            Segment.schedule_query[self.schedule] = {}
        Segment.schedule_query[self.schedule][self] = True

    def set_objects(self):
        Segment.objects[(self.joint, self.schedule, self.name)] = self

    def __repr__(self):
        return '<Segment {}>'.format(self.name)

    def __str__(self):
        return 'Segment {} for joint {}'.format(self.name, self.joint)

    def __lt__(self, other):
        return (self.joint, self.schedule, self.name) < (other.joint, other.schedule, other.name)

    def __le__(self, other):
        return (self.joint, self.schedule, self.name) <= (other.joint, other.schedule, other.name)

    def __eq__(self, other):
        return (self.joint, self.schedule, self.name) == (other.joint, other.schedule, other.name)

    def __ne__(self, other):
        return (self.joint, self.schedule, self.name) != (other.joint, other.schedule, other.name)

    def __gt__(self, other):
        return (self.joint, self.schedule, self.name) > (other.joint, other.schedule, other.name)

    def __ge__(self, other):
        return (self.joint, self.schedule, self.name) >= (other.joint, other.schedule, other.name)

    def __hash__(self):
        return hash((self.joint, self.schedule, self.name))

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

                # Add the StopSeq stop to segment.stops and StopSeq loc to segment.locs
                segment.stops[stop_seq.stop] = True
                if stop_seq.stop[:3] not in segment.locs:
                    segment.locs[stop_seq.stop[:3]] = []
                segment.locs[stop_seq.stop[:3]] = segment.locs.get(stop_seq.stop[:3]) + [stop_seq]

            segment.set_order()

    def get_json(self):
        attrs = dict([(k, getattr(self, k)) for k in ['joint', 'schedule', 'dir_order', 'dir_type', 'route', 'name']])
        attrs['direction'] = self.direction.id
        return attrs

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


class StopSeq(DataModelTemplate):

    json_path = '{}/data/stop_seq.json'.format(PATH)
    objects = {}
    segment_query = {}

    def set_object_attrs(self):
        self.gtfs_depart = self.arrive if self.destination else self.depart
        self.timedelta = datetime.timedelta(seconds=(self.depart - self.arrive))
        self.gtfs_timedelta = datetime.timedelta(seconds=(self.gtfs_depart - self.arrive))
        self.order = None

        if self.segment not in StopSeq.segment_query:
            StopSeq.segment_query[self.segment] = {}
        StopSeq.segment_query[self.segment][self] = True

    def set_objects(self):
        StopSeq.objects[(self.segment, self.load_seq)] = self

    def get_json(self):
        return dict([(k, getattr(self, k)) for k in ['segment', 'stop', 'arrive', 'depart', 'timed', 'display',
                                                     'load_seq', 'destination']])

