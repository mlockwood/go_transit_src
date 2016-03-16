

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
Main ------------------------------------------------------------------
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
    if not os.path.exists(System.path + '/reports/schedules/routes'):
        os.makedirs(System.path + '/reports/schedules/routes')

    # Build the master table
    master = build_master_table()

    # Iterate through each route
    for route in master:

        # Open workbook and worksheet
        workbook = xlsxwriter.Workbook(System.path + '/reports/schedules/' +
                                       'routes/' + route.lower() +
                                       '_schedule.xlsx')
        worksheet = workbook.add_worksheet('Schedule')
        # Set column widths
        worksheet.set_column('A:A', 20)
        worksheet.set_column('B:B', 36)
        worksheet.set_column('C:C', 36)

        # Format declarations
        merge_format = workbook.add_format({'bold': True,
                                            'align': 'center',
                                            'fg_color': '#D7E4BC',
                                            })
        bold_format = workbook.add_format({'bold': True,
                                           'align': 'center',
                                           })
        center_format = workbook.add_format({'align': 'center',
                                             'valign': 'vcenter',
                                             })
        stop_format = workbook.add_format({'bold': True,
                                           'align': 'center',
                                           'valign': 'vcenter',
                                           'text_wrap': True,
                                           })
        text_wrap_format = workbook.add_format({'text_wrap': True})

        # Write header
        worksheet.merge_range('A1:C1', route, merge_format)
        worksheet.write_row('A2', ['Stop', 'To ' + obj._dir1.title(),
            'To ' + obj._dir2.title()], bold_format)

        # Write data
        row = 3
        for stop in sorted(obj._records.keys()):
            #if Stop.objects[stop]._display == '0':
            #    continue
            worksheet.write('A' + str(row), str(st.Stop.obj_map[str(stop
                ).lower()]._name).title(), stop_format)
            # Add first direction times
            try:
                worksheet.write('B' + str(row), ', '.join(sorted(
                    obj._records[stop][obj._dir1])), text_wrap_format)
            except:
                worksheet.write('B' + str(row), '--', center_format)
            # Add second direction times
            try:
                worksheet.write('C' + str(row), ', '.join(sorted(
                    obj._records[stop][obj._dir2])), text_wrap_format)
            except:
                worksheet.write('C' + str(row), '--', center_format)
            row += 1

        # Close workbook
        workbook.close()
    return True


if __name__ == "__main__":
    publish()