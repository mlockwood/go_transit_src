#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

# Python libraries and packages
import copy
import csv
import datetime
import math
import os
import re

# Entire scripts from src
import src.scripts.transit.route.route as rt
import src.scripts.transit.route.constants as RouteConstants
import src.scripts.transit.route.errors as RouteErrors

# Classes and variables from src
from src.scripts.transit.constants import PATH


def build_master_table():
    master_table = {}

    # Build master_table
    for ST in rt.StopTime.objects:
        obj = rt.StopTime.objects[ST]

        # If stop_seq == 0, implying an origin, add to the table
        if int(obj.stop_seq) == 1:

            # Create the reference point of (route_id, dir_id)
            trip = rt.Trip.objects[obj.trip_id]
            point = (trip.route_id, trip.direction_id)

            # Prepare multiple dictionary layers for the master_table
            if obj.joint not in master_table:
                master_table[obj.joint] = {}
            if obj.driver not in master_table[obj.joint]:
                master_table[obj.joint][obj.driver] = {}
            if point not in master_table[obj.joint][obj.driver]:
                master_table[obj.joint][obj.driver][point] = []

            # Add stop_time to master_table [joint][driver][point] = [stop_time, ...]
            master_table[obj.joint][obj.driver][point] = master_table[obj.joint][obj.driver].get(point, 0) + [
                obj.departure]

    # Sort master_table lists
    for joint in master_table:
        for driver in master_table[joint]:
            for point in master_table[joint][driver]:
                master_table[joint][driver][point] = sorted(master_table[joint][driver].get(point, 0))

    return master_table


def publish():
    # Establish report directory for schedules
    if not os.path.exists(PATH + '/reports/routes/schedules/'):
        os.makedirs(PATH + '/reports/routes/schedules/')

    # Build the master table
    master = build_master_table()
    # Iterate through each joint_route
    for joint in master:
        print(joint, rt.JointRoute.objects[joint].display_order)

    return True


if __name__ == "__main__":
    publish()