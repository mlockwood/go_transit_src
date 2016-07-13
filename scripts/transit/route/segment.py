#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

# Python libraries and packages
import datetime

# Import scripts from src
import scripts.transit.stop.stop as st
from scripts.transit.route.direction import Direction
from scripts.transit.route.errors import *
from scripts.utils.IOutils import load_json, export_json

# Import variables from src
from scripts.transit.constants import PATH

# Load dependent data
Direction.load()


class Segment(object):

    objects = {}
    id_generator = 1

    def __init__(self, joint, time, dir_order, route, name, direction_id):
        # Initialized attributes
        self.joint = int(joint)
        self.time = int(time)
        self.dir_order = dir_order
        self.route = int(route)
        self.name = name
        self.direction = Direction.objects[int(direction_id)]
        self.direction_id = int(direction_id)

        # Attributes set after initialization
        self.trip_length = 0
        self.stop_seqs = {}
        self.seq_order = {}
        self.stops = {}

        # Add to objects
        Segment.objects[name] = self

    def __repr__(self):
        return '<Segment {}>'.format(self.name)

    def __str__(self):
        return 'Segment {} for route {} and direction {}'.format(self.name, self.route, self.direction)

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

    @staticmethod
    def order_segments():
        for obj in Segment.objects:
            Segment.objects[obj].set_order()

    @classmethod
    def load(cls):
        load_json('{}/data/routes/segments.json'.format(PATH), cls)

    @classmethod
    def export(cls):
        export_json('{}/data/routes/segments.json'.format(PATH), cls)

    def get_json(self):
        return dict([(k, getattr(self, k)) for k in ['joint', 'time', 'dir_order', 'route', 'name', 'direction_id']])

    def set_order(self):
        # List of stop_ids in order of travel_time
        temp = [self.seq_order[key] for key in sorted(self.seq_order.keys())]

        # Convert temp list to dictionary of segment order
        order = {}
        i = 0
        for row_id in temp:
            order[row_id] = i
            i += 1
        self.seq_order = order

        # Transfer order to stop_seq objects
        for stop_seq in self.stop_seqs:
            stop_seq.order = self.seq_order[stop_seq.load_seq]

        # Convert stop_seqs to stop_seqs[stop_seq] = StopSeq
        temp = {}
        for stop_seq in self.stop_seqs:
            temp[stop_seq.order] = stop_seq
        self.stop_seqs = temp

        return True


class StopSeq(object):

    objects = {}

    def __init__(self, segment, stop, gps_ref, arrive, depart, timed, display, load_seq, destination):
        # Stop validation
        if (stop, gps_ref) not in st.Point.objects:
            raise UnknownStopPointError('Stop {}{} from {} is not recognized.'.format(stop, gps_ref, segment))

        # Assign attributes
        self.segment = segment
        self.stop = stop
        self.gps_ref = gps_ref
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

        self.connect_segment()
        StopSeq.objects[(segment, load_seq)] = self

    @classmethod
    def load(cls):
        load_json(PATH + '/data/routes/stop_seqs.json', cls)
        Segment.order_segments()

    @classmethod
    def export(cls):
        export_json(PATH + '/data/routes/stop_seqs.json', cls)

    def get_json(self):
        return dict([(k, getattr(self, k)) for k in ['segment', 'stop', 'gps_ref', 'arrive', 'depart', 'timed',
                                                     'display', 'load_seq', 'destination']])

    def connect_segment(self):
        self.segment = Segment.objects[self.segment]

        # Ensure the StopSeq object is added to segment.stop_seqs
        self.segment.stop_seqs[self] = True

        # Add the StopSeq stop to segment.stops
        self.segment.stops[self.stop] = True

        # Verify that a duplicate arrival is not present
        if self.arrive in self.segment.seq_order:
            raise DuplicateTimingSpreadError('{} duplicate arrival time of {}'.format(self.segment.name, self.arrive))

        # Add order[arrival] = i
        self.segment.seq_order[self.arrive] = self.load_seq

        # If the destination is true, set current StopSeq's depart as the trip_length for the segment
        if self.destination:
            self.segment.trip_length = self.depart
        return True


Segment.load()
StopSeq.load()
print(len(Segment.objects))
Segment.export()
