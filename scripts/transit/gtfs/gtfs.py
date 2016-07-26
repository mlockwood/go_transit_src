#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

# Python libraries and packages
import datetime
import inspect
import shutil
import sys

# Entire scripts from src
from src.scripts.transit.stop.stop import Stop
from src.scripts.transit.route.route import DateRange
from src.scripts.transit.route.service import Holiday
from src.scripts.transit.constants import PATH
from src.scripts.utils.IOutils import *


__author__ = 'Michael Lockwood'
__github__ = 'mlockwood'
__projectclass__ = 'go'
__projectsubclass__ = 'transit'
__projectname__ = 'ridership.py'
__date__ = '20160404'
__credits__ = None
__collaborators__ = None


DATA_PATH = '{}/data'.format(PATH)
GTFS_PATH = '{}/reports/gtfs/files'.format(PATH)
set_directory(GTFS_PATH)
feed = DateRange.get_feed_by_date(datetime.datetime.today())  # Change the datetime to select a different feed


class Feed(object):

    file = ''
    path = GTFS_PATH


class ConvertFeed(Feed):

    booleans = True
    header = []
    json_file = ''
    order = None

    @classmethod
    def create_feed(cls):
        if not cls.json_file:
            cls.json_file = '{}/{}.json'.format(DATA_PATH, cls.file)
        json_to_txt(cls.json_file, '{}/{}.txt'.format(cls.path, cls.file), header=cls.header,
                    order=cls.order if cls.order else cls.header, booleans=cls.booleans)


class ExportFeed(Feed):

    @classmethod
    def create_feed(cls):
        txt_writer(cls.get_matrix(), '{}/{}.txt'.format(cls.path, cls.file))
        return True

    @classmethod
    def get_matrix(cls):
        pass


class BuildAgency(ConvertFeed):

    file = 'agency'
    header = ['agency_id', 'agency_name', 'agency_url', 'agency_timezone', 'agency_lang', 'agency_phone']


class BuildCalendar(ConvertFeed):

    booleans = False
    file = 'calendar'
    json_file = '{}/{}.json'.format(DATA_PATH, 'service')
    header = ['service_id', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday', 'start_date',
              'end_date']
    order = ['id', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday', 'start_date',
             'end_date']


class BuildHolidays(ExportFeed):

    file = 'calendar_dates'

    @classmethod
    def get_matrix(cls):
        holidays = [['service_id', 'date', 'exception_type']]
        Holiday.load()
        holidays += Holiday.get_holidays()
        return holidays


class BuildRoutes(ConvertFeed):

    file = 'routes'
    header = ['route_id', 'route_short_name', 'route_long_name', 'route_desc', 'route_type', 'route_color',
              'route_text_color']


class BuildStops(ExportFeed):

    file = 'stops'

    @classmethod
    def get_matrix(cls):
        stops = [['stop_id', 'stop_name', 'stop_desc', 'stop_lat', 'stop_lon']]
        for obj in Stop.objects:
            stop = Stop.objects[obj]
            if stop.available == '1':
                stops.append([stop.id, stop.name, stop.description, stop.lat, stop.lng])
        return stops


class BuildStopTimes(ExportFeed):

    file = 'stop_times'

    @classmethod
    def get_matrix(cls):
        stop_times = [['trip_id', 'arrival_time', 'departure_time', 'stop_id', 'stop_sequence', 'pickup_type',
                       'drop_off_type', 'timepoint']]
        for stoptime in feed[1]:
            if len(stoptime.trip.stop_times) > 1:
                stop_times.append([stoptime.trip.id, stoptime.arrive_24p, stoptime.gtfs_depart_24p, stoptime.stop,
                                   stoptime.order, stoptime.pickup, stoptime.dropoff, stoptime.timepoint])
        return stop_times


class BuildTransfers(ConvertFeed):

    file = 'transfers'
    header = ['from_stop_id', 'to_stop_id', 'transfer_type']


class BuildTrips(ExportFeed):

    file = 'trips'

    @classmethod
    def get_matrix(cls):
        trips = [['route_id', 'service_id', 'trip_id', 'direction_id', 'block_id', 'shape_id']]
        for trip in feed[0]:
            if len(trip.stop_times) > 1:
                trips.append([trip.segment.route, trip.joint.service.id, trip.id, trip.segment.dir_type_num,
                              trip.driver.position, trip.direction.id])
        return trips


def create_gtfs():
    clsmembers = inspect.getmembers(sys.modules[__name__], inspect.isclass)
    for cls in clsmembers:
        if re.search('Build', cls[0]) and re.search('__main__', str(cls[1])):
            cls[1].create_feed()


if __name__ == "__main__":
    create_gtfs()
    try:
        shutil.rmtree('{}/src/gtfs'.format(PATH))
    except OSError:
        pass
    finally:
        shutil.copytree(GTFS_PATH, '{}/src/gtfs'.format(PATH))
