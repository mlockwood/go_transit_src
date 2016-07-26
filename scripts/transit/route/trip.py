import csv
import datetime
import os

from src.scripts.transit.constants import PATH
from src.scripts.utils.time import convert_to_24_plus_time
from src.scripts.transit.route.constants import STOP_TIME_HEADER
from src.scripts.utils.IOutils import load_json, export_json


class Trip(object):

    objects = {}
    id_generator = {}

    def __init__(self, joint, schedule, segment, stop_seqs, start_loc, end_loc, start_time, driver):
        # Establish id
        self.joint = joint
        self.schedule = schedule
        self.segment = segment
        self.direction = segment.direction
        self.trip_seq = segment.trip_generator
        self.id = '-'.join(str(s) for s in [joint.id, schedule.id, segment.name, self.trip_seq])
        segment.trip_generator += 1

        # Develop times, stop_times, and driver
        self.start_loc = start_loc  # This is Segment loc not RouteGraph loc
        self.end_loc = end_loc  # This is Segment loc not RouteGraph loc
        self.base_time = start_time - datetime.timedelta(seconds=start_loc)
        self.start_time = start_time  # This must have gone to the next date if it passed midnight
        self.end_time = self.base_time + datetime.timedelta(seconds=end_loc)
        self.stop_times = dict((StopTime(self, stop_seq, self.base_time), True) for stop_seq in stop_seqs)
        self.driver = driver
        self.driver_id = driver.id
        Trip.objects[self.id] = self

    def __repr__(self):
        return '<Trip {} with Segment {}>'.format(self.id, self.segment.name)

    def __lt__(self, other):
        return (self.id, self.segment.name) < (other.id, other.segment.name)

    def __le__(self, other):
        return (self.id, self.segment.name) <= (other.id, other.segment.name)

    def __eq__(self, other):
        return (self.id, self.segment.name) == (other.id, other.segment.name)

    def __ne__(self, other):
        return (self.id, self.segment.name) != (other.id, other.segment.name)

    def __gt__(self, other):
        return (self.id, self.segment.name) > (other.id, other.segment.name)

    def __ge__(self, other):
        return (self.id, self.segment.name) >= (other.id, other.segment.name)

    def __hash__(self):
        return hash((self.id, self.segment.name))

    @classmethod
    def export(cls):
        export_json('{}/data/trip.json'.format(PATH), cls)

    def get_json(self):
        attrs = dict([(k, getattr(self, k)) for k in ['id', 'start_loc', 'end_loc', 'driver_id']])
        attrs['joint'] = self.joint.id
        attrs['schedule'] = self.schedule.id
        attrs['segment'] = self.segment.name
        attrs['base_time'] = self.base_time.strftime('%Y%m%d-%H%M%S')
        attrs['start_time'] = self.start_time.strftime('%Y%m%d-%H%M%S')
        attrs['end_time'] = self.end_time.strftime('%Y%m%d-%H%M%S')
        return attrs


class StopTime(object):

    objects = {}

    def __init__(self, trip, stop_seq, base_time):
        # Attributes from __init__
        self.trip = trip
        self.trip_id = trip.id
        self.stop_seq = stop_seq

        # Attributes from stop_seq
        self.stop = stop_seq.stop

        # Times for the StopTime, the first three can be made to strings with .strftime('%H:%M:%S')
        self.arrive = base_time + datetime.timedelta(seconds=stop_seq.arrive)
        self.depart = base_time + datetime.timedelta(seconds=stop_seq.depart)
        self.gtfs_depart = base_time + datetime.timedelta(seconds=stop_seq.gtfs_depart)
        self.arrive_24p = convert_to_24_plus_time(self.trip.joint.service.start_date, self.arrive)
        self.depart_24p = convert_to_24_plus_time(self.trip.joint.service.start_date, self.depart)
        self.gtfs_depart_24p = convert_to_24_plus_time(self.trip.joint.service.start_date, self.gtfs_depart)
        self.arrive = self.arrive.strftime('%H:%M:%S')
        self.depart = self.depart.strftime('%H:%M:%S')
        self.gtfs_depart = self.gtfs_depart.strftime('%H:%M:%S')

        self.order = stop_seq.order
        self.timepoint = stop_seq.timed
        self.pickup = 3 if not self.timepoint else 0
        self.dropoff = 3 if not self.timepoint else 0
        self.display = stop_seq.display

        # Set records
        StopTime.objects[(trip.id, self.order)] = self

    def get_record(self):
        return [self.trip.id, self.stop, self.trip.direction.name, self.arrive, self.gtfs_depart, self.order,
                self.timepoint, self.pickup, self.dropoff, self.display, self.trip.driver.position]

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

    @classmethod
    def export(cls):
        export_json('{}/data/stop_time.json'.format(PATH), cls)

    def get_json(self):
        return dict([(k, getattr(self, k)) for k in ['trip_id', 'stop', 'arrive', 'depart', 'gtfs_depart', 'arrive_24p',
                                                     'depart_24p', 'gtfs_depart_24p', 'order', 'timepoint', 'pickup',
                                                     'dropoff', 'display']])

