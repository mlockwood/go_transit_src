#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

# Python libraries and packages
import csv
import datetime
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
    writer = open('{}/reports/gtfs/files/{}.txt'.format(PATH, re.sub('build_', '', func.__name__)), 'w')

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
        if st.convert_gps_dms_to_dd(stop.gps_n) and st.convert_gps_dms_to_dd(stop.gps_w) and stop.available == '1':
            stops.append([stop.stop_id + stop.gps_ref, stop.name, stop.desc, st.convert_gps_dms_to_dd(stop.gps_n),
                          st.convert_gps_dms_to_dd(stop.gps_w)])
    return stops


@txt_writer
def build_routes():
    routes = [['route_id', 'route_short_name', 'route_long_name', 'route_desc', 'route_type', 'route_color',
               'route_text_color']]
    for obj in rt.Route.objects:
        route = rt.Route.objects[obj]
        routes.append([route.id, route.short, route.name, route.desc, '3', route.color, route.text_color])
    return routes


@txt_writer
def build_trips():
    trips = [['route_id', 'service_id', 'trip_id', 'direction_id', 'block_id', 'shape_id']]
    for obj in rt.Trip.objects:
        trip = rt.Trip.objects[obj]
        if len(trip.stop_times) > 1:
            trips.append([trip.route_id, trip.service_id, trip.id, trip.segment.dirnum, trip.driver, trip.direction_id])
    return trips


@txt_writer
def build_stop_times():
    stop_times = [['trip_id', 'arrival_time', 'departure_time', 'stop_id', 'stop_sequence', 'pickup_type',
                   'drop_off_type', 'timepoint']]
    for obj in rt.StopTime.objects:
        stop_time = rt.StopTime.objects[obj]
        if len(stop_time.trip.stop_times) > 1:
            stop_times.append([stop_time.trip.id, stop_time.arrive_24p, stop_time.gtfs_depart_24p,
                               '{}{}'.format(stop_time.stop_id, stop_time.gps_ref), stop_time.order, stop_time.pickup,
                               stop_time.dropoff, stop_time.timepoint])
    return stop_times


@txt_writer
def build_calendar():
    calendars = [['service_id', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
                 'start_date', 'end_date']]
    for obj in rt.Service.objects:
        service = rt.Service.objects[obj]
        calendars.append([service.id, service.monday, service.tuesday, service.wednesday, service.thursday,
                          service.friday, service.saturday, service.sunday, service.start_date.strftime('%Y%m%d'),
                          service.end_date.strftime('%Y%m%d')])
    return calendars


@txt_writer
def build_calendar_dates():
    dates = [['service_id', 'date', 'exception_type']]
    holidays = csv.reader(open('{}/data/routes/holidays.csv'.format(PATH), 'r', newline=''), delimiter=',',
                          quotechar='|')
    for row in holidays:
        if re.search('[a-zA-Z]', row[0]):
            continue
        for obj in rt.Service.objects:
            service = rt.Service.objects[obj]
            # Check if the holiday applies to the given service dates
            if service.start_date <= datetime.datetime.strptime(row[0], '%Y%m%d') <= service.end_date:
                dates.append([service.id, row[0], 2])
    return dates


if __name__ == "__main__":
    shutil.copyfile('{}/data/agency/agency.txt'.format(PATH), '{}/reports/gtfs/files/agency.txt'.format(PATH))
    shutil.copyfile('{}/data/routes/transfers.txt'.format(PATH), '{}/reports/gtfs/files/transfers.txt'.format(PATH))
    try:
        shutil.rmtree('{}/src/gtfs')
    except OSError:
        pass
    finally:
        shutil.copytree('{}/reports/gtfs/files', '{}/src/gtfs')
