#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

# Python libraries and packages
import datetime
import inspect
import sys

import src.scripts.gtfs.shape_kml as shape_kml
import src.scripts.gtfs.validate_shape_kml as validate_shape_kml
from src.scripts.route.route import load
from src.scripts.route.service import Holiday
from src.scripts.constants import *
from src.scripts.utils.IOutils import *


__author__ = 'Michael Lockwood'
__github__ = 'mlockwood'
__projectclass__ = 'go'
__projectsubclass__ = 'transit'
__projectname__ = 'ridership.py'
__date__ = '20160404'
__credits__ = None
__collaborators__ = None


GTFS_PATH = '{}/reports/gtfs/files'.format(PATH)
set_directory(GTFS_PATH)


class Feed(object):

    file = ''
    path = GTFS_PATH



class ConvertFeed(Feed):

    booleans = True
    conversions = {}
    file = ''
    filtered = {}
    header = []
    json_file = ''
    order = None
    defaults = {}

    @classmethod
    def create_feed(cls):
        json_to_txt(cls.json_file, '{}/{}.txt'.format(cls.path, cls.file), header=cls.header,
                    order=cls.order if cls.order else cls.header, booleans=cls.booleans, defaults=cls.defaults,
                    conversions=cls.conversions, filtered=cls.filtered)


class ExportFeed(Feed):

    feed = None

    @classmethod
    def create_feed(cls):
        txt_writer(cls.get_matrix(), '{}/{}.txt'.format(cls.path, cls.file))
        return True

    @classmethod
    def get_matrix(cls):
        pass



class BuildAgency(ConvertFeed):

    file = 'agency'
    json_file = '{}/agency/agency.json'.format(DATA_PATH)
    header = ['agency_id', 'agency_name', 'agency_url', 'agency_timezone', 'agency_lang', 'agency_phone']
    order = ['id', 'name', 'url', 'timezone', 'lang', 'phone']



class BuildCalendar(ConvertFeed):

    booleans = False
    file = 'calendar'
    json_file = '{}/route/service.json'.format(DATA_PATH)
    header = ['service_id', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday', 'start_date',
              'end_date']
    conversions = {'start_date': ['-', ''], 'end_date': ['-', '']}


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
    json_file = '{}/route/route.json'.format(DATA_PATH)
    header = ['route_id', 'route_short_name', 'route_long_name', 'route_desc', 'route_type', 'route_color',
              'route_text_color']
    order = ['id', 'short_name', 'long_name', 'description', 'route_type', 'color', 'text_color']
    defaults = {'route_type': 3}


class BuildStops(ConvertFeed):

    file = 'stops'
    json_file = '{}/stop/stop.json'.format(DATA_PATH)
    header = ['stop_id', 'stop_name', 'stop_desc', 'stop_lat', 'stop_lon']
    order = ['id', 'name', 'description', 'lat', 'lng']
    filtered = {'available': {1: True}}


class BuildStopTimes(ExportFeed):

    file = 'stop_times'

    @classmethod
    def get_matrix(cls):
        stop_times = [['trip_id', 'arrival_time', 'departure_time', 'stop_id', 'stop_sequence', 'pickup_type',
                       'drop_off_type', 'timepoint']]
        temp = {}
        for stoptime in cls.feed:
            temp[stoptime.id] = [stoptime.trip.id, stoptime.arrive_24p, stoptime.gtfs_depart_24p, stoptime.stop,
                                 stoptime.order, stoptime.pickup, stoptime.dropoff, stoptime.timepoint]
        for stoptime in temp:
            stop_times.append(temp[stoptime])
        return stop_times


class BuildTrips(ExportFeed):

    file = 'trips'

    @classmethod
    def get_matrix(cls):
        trips = [['route_id', 'service_id', 'trip_id', 'trip_headsign', 'direction_id', 'block_id', 'shape_id']]
        for trip in cls.feed:
            trips.append([trip.route, trip.service, trip.id, trip.head_sign, trip.direction, trip.driver, trip.segment])
        return trips


def create_gtfs(date=datetime.datetime.today()):
    BuildTrips.feed, BuildStopTimes.feed = load(date)
    clsmembers = inspect.getmembers(sys.modules[__name__], inspect.isclass)
    for cls in clsmembers:
        if re.search('Build', cls[0]) and re.search('__main__', str(cls[1])):
            cls[1].create_feed()
    shape_kml.process()
    validate_shape_kml.validate()


if __name__ == "__main__":
    create_gtfs()
