#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

# Python libraries and packages
import shutil
import xlsxwriter

# Entire scripts from src
from src.scripts.route.route import *
from src.scripts.stop.stop import Stop
from src.scripts.route.constants import *

# Classes and variables from src
from src.scripts.constants import *
from src.scripts.utils.IOutils import *


def build_master_table(date):
    master_table = {}

    # Build master_table
    for stoptime in load(date)[1]:

        # If the point is a timepoint, add to the table
        if int(stoptime.timepoint) == 1:
            driver = stoptime.trip.driver
            if driver not in master_table:
                master_table[driver] = []
            master_table[driver] = master_table.get(driver) + [[stoptime.stop, Stop.objects[stoptime.stop].name,
                                                                stoptime.trip.head_sign, stoptime.depart]]

    return master_table


def publish_timepoints(date):
    # Delete existing timepoints before creating new ones
    try:
        shutil.rmtree('{}/route/timepoints/'.format(PATH))
    except OSError:
        pass
    finally:
        set_directory('{}/route/timepoints/'.format(REPORT_PATH))

    master = build_master_table(date)
    date_range = DateRange.get_obj_by_date(date)

    # Iterate through each joint_route
    for driver in master:
        if isinstance(driver, Driver):
            driver = driver.id
        position = date_range.lookup[str(driver)]
        start = Driver.objects[driver].start

        # Open workbook and worksheet
        workbook = xlsxwriter.Workbook('{}/route/timepoints/timepoints_{}.xlsx'.format(REPORT_PATH, position))
        worksheet = workbook.add_worksheet('Timepoints {}'.format(position))

        # Set column widths
        worksheet.set_column('A:A', 8)
        worksheet.set_column('B:B', 30)
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
        worksheet.merge_range('A1:D1', 'Timepoints for Driver Position {}'.format(position), merge_format)
        worksheet.merge_range('A2:D2', 'Starting Location: {} {}'.format(start, Stop.objects[start].name), start_format)
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
    publish_timepoints(datetime.datetime.today())
