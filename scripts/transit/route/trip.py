import csv
import datetime
import os

from src.scripts.constants import *
from src.scripts.utils.classes import DataModelTemplate
from src.scripts.utils.IOutils import set_directory
from src.scripts.utils.time import convert_to_24_plus_time
from src.scripts.transit.route.constants import STOP_TIME_HEADER
from src.scripts.transit.route.direction import Direction


Direction.load()


class Trip(DataModelTemplate):

    feed = {}
    json_path = '{}/data/trip.json'.format(PATH)
    objects = {}

    def __repr__(self):
        return '<Trip {}>'.format(self.id)

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

    # Expect these __init__ args => id, direction.id, start_loc, end_loc, start_time, driver.id
    def set_object_attrs(self):
        self.direction = Direction.objects[self.direction]
        self.start_time = datetime.datetime.strptime(self.start_time, '%Y-%m-%d %H:%M:%S')  # Added +1 day if > 12:00
        self.base_time = self.start_time - datetime.timedelta(seconds=self.start_loc)
        self.end_time = self.base_time + datetime.timedelta(seconds=self.end_loc)

        # Set trip in schedule's feed
        if self.schedule not in Trip.feed:
            Trip.feed[self.schedule] = {}
        Trip.feed[self.schedule][self] = True

    def create_stop_times(self, stop_seqs, service):
        return dict((StopTime(**{
            'id': '{}:{}'.format(self.id, str(stop_seq.order)),
            'trip': self.id,
            'base_time': self.base_time,
            'stop_seq': stop_seq,
            'service': service
        }), True) for stop_seq in stop_seqs)

    def get_json(self):
        attrs = dict([(k, getattr(self, k)) for k in ['id', 'schedule', 'start_loc', 'end_loc']])
        attrs['direction'] = self.direction.id
        attrs['start_time'] = self.start_time.strftime('%Y-%m-%d %H:%M:%S')
        attrs['driver'] = self.driver.id
        return attrs


class StopTime(DataModelTemplate):

    feed = {}
    json_path = '{}/data/stop_time.json'.format(PATH)
    objects = {}

    # Expect these __init__ args => id, trip.id
    # Option A => base_time, stop_seq, service; B => all attrs except stop_seq from set_object_attrs
    def set_object_attrs(self):
        self.trip = Trip.objects[self.trip]

        if 'stop_seq' in self.__dict__:
            # Attributes from stop_seq
            self.stop = self.stop_seq.stop
            self.order = self.stop_seq.order
            self.timepoint = self.stop_seq.timed
            self.pickup = 3 if not self.timepoint else 0
            self.dropoff = 3 if not self.timepoint else 0
            self.display = self.stop_seq.display

            # Times for the StopTime, the first three can be made to strings with .strftime('%H:%M:%S')
            self.arrive = self.base_time + datetime.timedelta(seconds=self.stop_seq.arrive)
            self.depart = self.base_time + datetime.timedelta(seconds=self.stop_seq.depart)
            self.gtfs_depart = self.base_time + datetime.timedelta(seconds=self.stop_seq.gtfs_depart)
            self.arrive_24p = convert_to_24_plus_time(self.service.start_date, self.arrive)
            self.depart_24p = convert_to_24_plus_time(self.service.start_date, self.depart)
            self.gtfs_depart_24p = convert_to_24_plus_time(self.service.start_date, self.gtfs_depart)
            self.arrive = self.arrive.strftime('%H:%M:%S')
            self.depart = self.depart.strftime('%H:%M:%S')
            self.gtfs_depart = self.gtfs_depart.strftime('%H:%M:%S')

            # Get rid of base_time, stop_seq, and service to prevent them from being exported and loaded
            delattr(self, 'base_time')
            delattr(self, 'stop_seq')
            delattr(self, 'service')

        # Set trip in schedule's feed
        if self.trip.schedule not in StopTime.feed:
            StopTime.feed[self.trip.schedule] = {}
        StopTime.feed[self.trip.schedule][self] = True

    def get_record(self):
        return [self.trip.id, self.stop, self.trip.direction.name, self.arrive, self.gtfs_depart, self.order,
                self.timepoint, self.pickup, self.dropoff, self.display, self.trip.driver.position]

    @staticmethod
    def publish_matrix():
        set_directory('{}/routes'.format(REPORT_PATH))
        writer = csv.writer(open('{}/routes/records.csv'.format(REPORT_PATH), 'w', newline=''), delimiter=',',
                            quotechar='|')
        writer.writerow(STOP_TIME_HEADER)
        for stop_time in sorted(StopTime.objects):
            writer.writerow(StopTime.objects[stop_time].get_record())
        return True

    def get_json(self):
        self.trip = self.trip.id
        return dict((k, getattr(self, k)) for k in self.__dict__)

