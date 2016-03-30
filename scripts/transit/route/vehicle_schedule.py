

import os
import re
import xlsxwriter


"""
GO Imports-------------------------------------------------------------
"""
import src.scripts.transit.constants as System
import src.scripts.transit.route.route as rt
import src.scripts.transit.stop.stop as st

"""
Main Class-------------------------------------------------------------
"""




def build_master_table():
    master_table = {}

    # Build master_table
    for ST in rt.StopTime.objects:
        obj = rt.StopTime.objects[ST]

        # Remove objects who have a display value of 0
        if obj.display == 0:
            continue

        # Set master table value [route][stop][direction] = [times]
        if obj.route not in master_table:
            master_table[obj.route] = {}
        if obj.stop_id not in master_table[obj.route]:
            master_table[obj.route][obj.stop_id] = {}
        if obj.direction not in master_table[obj.route][obj.stop_id]:
            master_table[obj.route][obj.stop_id][obj.direction] = []
        master_table[obj.route][obj.stop_id][obj.direction].append(obj.time)

    # Sort master_table values
    for route in master_table:
        for stop in master_table[route]:
            for direction in master_table[route][stop]:
                master_table[route][stop][direction] = sorted(
                    master_table[route][stop].get(direction, 0))

    return master_table

def publish():
    # Establish report directory for schedules
    if not os.path.exists(System.path + '/reports/routes/schedules/'):
        os.makedirs(System.path + '/reports/routes/schedules/')

    # Build the master table
    master = build_master_table()

    # Iterate through each route

    return True


JointRoute.load_routes()
if __name__ == "__main__":
    publish()