#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

# Python libraries and packages
import os
import xlsxwriter

# Entire scripts from src
import scripts.transit.route.route as rt
import scripts.transit.stop.stop as st
import scripts.transit.route.constants as RouteConstants
import scripts.transit.route.errors as RouteErrors

# Classes and variables from src
from scripts.transit.constants import PATH


def build_master_table():
    master_table = {}

    # Build master_table
    for ST in rt.StopTime.objects:
        stoptime = rt.StopTime.objects[ST]

        # If the point is a timepoint, add to the table
        if int(stoptime.timepoint) == 1:

            if stoptime.driver not in master_table:
                master_table[stoptime.driver] = []
            master_table[stoptime.driver] = master_table.get(stoptime.driver) + [
                [stoptime.stop_id, st.Stop.obj_map[stoptime.stop_id].name, 'TO {}'.format(stoptime.direction),
                 stoptime.depart]]

    return master_table


def publish():
    # Establish report directory for schedules
    if not os.path.exists(PATH + '/reports/routes/vehicle_schedules/'):
        os.makedirs(PATH + '/reports/routes/vehicle_schedules/')

    # Build the master table
    master = build_master_table()
    # Iterate through each joint_route
    for driver in master:
        # Open workbook and worksheet
        workbook = xlsxwriter.Workbook(PATH + '/reports/routes/vehicle_schedules/schedule_{}.xlsx'.format(driver))
        worksheet = workbook.add_worksheet('Schedule {}'.format(driver))

        # Set column widths
        worksheet.set_column('A:A', 8)
        worksheet.set_column('B:B', 24)
        worksheet.set_column('C:C', 30)
        worksheet.set_column('D:D', 12)

        # Format declarations
        merge_format = workbook.add_format({'font_size': '20',
                                            'align': 'center',
                                            })
        start_format = workbook.add_format({'italic': True,
                                            'align': 'center',
                                            })
        bold_format = workbook.add_format({'bold': True,
                                           'align': 'center',
                                           'fg_color': '#D7E4BC',
                                           })
        even_format = workbook.add_format({'fg_color': '#F3F3F3'
                                           })

        # Write header
        start = rt.Driver.objects[driver].start
        worksheet.merge_range('A1:D1', 'Vehicle Schedule for Driver {}'.format(driver), merge_format)
        worksheet.merge_range('A2:D2', 'Starting Location: {} {}'.format(start, st.Stop.obj_map[start].name),
                              start_format)
        worksheet.write_row('A3', ['Stop ID', 'Stop Name', 'Direction', 'Departure'], bold_format)

        # Write data
        row = 4
        for stoptime in sorted(master[driver], key=lambda x: x[3]):
            if row % 2 == 1:
                worksheet.write_row('A{}'.format(row), stoptime, even_format)
            else:
                worksheet.write_row('A{}'.format(row), stoptime)
            row += 1

        # Close workbook
        workbook.close()

    return True


if __name__ == "__main__":
    publish()