#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

# Python libraries and packages
import os
import re
import shutil

# Entire scripts from src
import src.scripts.transit.stop.stop as st
import src.scripts.transit.route.route as rt

# Classes and variables from src
from src.scripts.transit.constants import PATH, BEGIN, BASELINE, INCREMENT


__author__ = 'Michael Lockwood'
__github__ = 'mlockwood'
__projectclass__ = 'go'
__projectsubclass__ = 'transit'
__projectname__ = 'ridership.py'
__date__ = '20160404'
__credits__ = None
__collaborators__ = None


def txt_writer(func):
    # Set up directories and files
    if not os.path.isdir(PATH + '/reports/gtfs'):
        os.makedirs(PATH + '/reports/gtfs')
    writer = open('{}/reports/gtfs/{}.txt'.format(PATH, re.sub('build_', '', func.__name__)), 'w')

    # Call inner function
    matrix = func()

    # Write header
    writer.write('{}\n'.format(','.join(str(s) for s in matrix[0])))
    # Write rows
    for row in sorted(matrix[1:]):
        writer.write('{}\n'.format(','.join(str(s) for s in row)))
    writer.close()
    return True


@txt_writer
def build_stops():
    stops = [['stop_id', 'stop_name', 'stop_desc', 'stop_lat', 'stop_lon']]
    for obj in st.Point.objects:
        stop = st.Point.objects[obj]
        stops.append([stop.stop_id + stop.gps_ref, stop.name, stop.desc, st.convert_gps_dms_to_dd(stop.gps_n),
                      st.convert_gps_dms_to_dd(stop.gps_w)])
    return stops


@txt_writer
def build_routes():
    routes = [['route_id', 'route_short_name', 'route_desc', 'route_type', 'route_color']]
    for obj in rt.Route.objects:
        route = rt.Route.objects[obj]
        routes.append([route.id, route.name, route.desc, '3', route.color])
    return routes


@txt_writer
def build_trips():
    trips = [['route_id', 'service_id', 'trip_id', 'direction_id']]
    for obj in rt.Trip.objects:
        trip = rt.Trip.objects[obj]
        trips.append([trip.route_id, trip.service_id, trip.id, trip.direction_id])
    return trips


@txt_writer
def build_stop_times():
    stop_times = [['trip_id', 'arrival_time', 'departure_time', 'stop_id', 'stop_sequence', 'pickup_type',
                   'drop_off_type', 'timepoint']]
    for obj in rt.StopTime.objects:
        stop_time = rt.StopTime.objects[obj]
        stop_times.append([stop_time.trip_id, stop_time.arrival, stop_time.departure, stop_time.stop_id,
                           stop_time.stop_seq, stop_time.pickup, stop_time.dropoff, stop_time.timepoint])
    return stop_times


@txt_writer
def build_calendar():
    calendars = [['service_id', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
                 'start_date', 'end_date']]
    for obj in rt.Service.objects:
        service = rt.Service.objects[obj]
        calendars.append([service.id] + [v for k, v in sorted(service.days.items())] + [service.start_date,
                                                                                        service.end_date])
    return calendars


if __name__ == "__main__":
    shutil.copyfile(PATH + '/data/agency/agency.txt', PATH + '/reports/gtfs/agency.txt')
    shutil.copyfile(PATH + '/data/agency/feed_info.txt', PATH + '/reports/gtfs/feed_info.txt')