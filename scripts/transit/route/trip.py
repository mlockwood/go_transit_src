import csv
import os

from ..constants import PATH
from ...utils.time import convert_to_24_plus_time
from .constants import STOP_TIME_HEADER


class Trip(object):

    objects = {}

    def __init__(self, route_id, service_id, direction_id, trip_seq, segment):
        self.route_id = route_id
        self.service_id = service_id
        self.direction_id = direction_id
        self.trip_seq = str(trip_seq)
        self.id = '-'.join([route_id, service_id, direction_id, self.trip_seq])
        self.segment = segment
        self.stop_times = {}
        self.driver = None
        Trip.objects[self.id] = self

    def __repr__(self):
        return '<Trip {} with Segment {}>'.format(self.id, self.segment)


class StopTime(object):

    objects = {}

    def __init__(self, trip_id, stop_seq, arrive):
        # Attributes from __init__
        self.trip = Trip.objects[trip_id]
        self.stop_seq = stop_seq

        # Attributes from stop_seq
        self.stop_id = stop_seq.stop
        self.gps_ref = stop_seq.gps_ref

        self.arrive = arrive.strftime('%H:%M:%S')
        self.depart = (arrive + stop_seq.timedelta).strftime('%H:%M:%S')
        self.gtfs_depart = (arrive + stop_seq.gtfs_timedelta).strftime('%H:%M:%S')
        self.arrive_24p = convert_to_24_plus_time(self.trip.segment.start, arrive)
        self.depart_24p = convert_to_24_plus_time(self.trip.segment.start, (arrive + stop_seq.timedelta))
        self.gtfs_depart_24p = convert_to_24_plus_time(self.trip.segment.start, (arrive + stop_seq.gtfs_timedelta))

        self.order = stop_seq.order
        self.timepoint = stop_seq.timed
        self.pickup = 3 if not self.timepoint else 0
        self.dropoff = 3 if not self.timepoint else 0
        self.display = stop_seq.display
        self.driver = 0
        self.joint = None

        # Attributes from trip_id
        self.route = self.trip.route
        self.direction = Trip.objects[trip_id].direction

        # Set records
        self.trip.stop_times[self.order] = self.stop_id
        StopTime.objects[(trip_id, self.order)] = self

    def get_record(self):
        return [self.trip.id, self.stop_id, self.gps_ref, self.direction.name, self.arrive, self.gtfs_depart,
                self.order, self.timepoint, self.pickup, self.dropoff, self.display, self.driver, self.joint]

    @staticmethod
    def publish_matrix():
        if not os.path.exists(PATH + '/reports/routes'):
            os.makedirs(PATH + '/reports/routes')
        writer = csv.writer(open('{}/reports/routes/records.csv'.format(PATH), 'w', newline=''), delimiter=',',
                            quotechar='|')
        writer.writerow(STOP_TIME_HEADER)
        for stop_time in sorted(StopTime.objects):
            writer.writerow(StopTime.objects[stop_time].get_record())
        return True

    # Export JSON instead?
