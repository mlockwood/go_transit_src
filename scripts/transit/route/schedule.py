

import os
import re
import xlsxwriter


"""
GO Imports-------------------------------------------------------------
"""
import src.scripts.transit.constants as System
import src.scripts.transit.route.route as rt
import src.scripts.transit.stop.stop as st

import src.scripts.transit.route.errors as RouteErrors

"""
Main ------------------------------------------------------------------
"""
def build_master_table():
    master_table = {}

    # Build master_table
    for ST in rt.StopTime.objects:
        obj = rt.StopTime.objects[ST]

        # Remove objects who have a display value of 0
        if str(obj.display) == '0':
            continue

        # Set master table as [route][stop][direction] = [times]
        if obj.route not in master_table:
            master_table[obj.route] = {}
        if obj.stop_id not in master_table[obj.route]:
            master_table[obj.route][obj.stop_id] = {}
        if obj.direction not in master_table[obj.route][obj.stop_id]:
            master_table[obj.route][obj.stop_id][obj.direction] = []
        master_table[obj.route][obj.stop_id][obj.direction].append(obj.time)

    # Sort master_table times
    for route in master_table:
        for stop in master_table[route]:
            for direction in master_table[route][stop]:
                master_table[route][stop][direction] = sorted(
                    master_table[route][stop].get(direction, 0))

    # If route has a headway divisible by 60 without remainder, use XX notation instead of all stops
    for route in master_table:
        if 60 % route.headway == 0:
            count = 60 / route.headway
            for stop in master_table[route]:
                cur_count = count * int(route.display[stop])
                for direction in master_table[route][stop]:
                    i = 0
                    new_times = []
                    for time in master_table[route][stop][direction]:
                        if i == cur_count:
                            break
                        new_times.append('xx:' + time[-2:])
                        i += 1
                    master_table[route][stop][direction] = sorted(new_times)

    return master_table


def publish():
    # Establish report directory for schedules
    if not os.path.exists(System.path + '/reports/routes/schedules'):
        os.makedirs(System.path + '/reports/routes/schedules')

    # Build the master table
    master = build_master_table()

    # Iterate through each route
    for route in master:

        # Open workbook and worksheet
        workbook = xlsxwriter.Workbook(System.path + '/reports/routes/schedules/' + re.sub(' ', '_', route.name) +
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
        worksheet.merge_range('A1:C1', route.name, merge_format)
        worksheet.write_row('A2', ['Stop', 'To ' + route.direction0.name, 'To ' + route.direction1.name], bold_format)

        # Write data
        row = 3
        for stop in sorted(route.schedule.keys()):
            stop_id = route.schedule[stop]

            # Verify stop was added to the master table, if not continue
            if stop_id not in master[route]:
                continue

            # Write stop name in the first column
            worksheet.write('A' + str(row), str(st.Stop.obj_map[stop_id].name), stop_format)

            # Add first direction times
            if route.direction0 in master[route][stop_id]:
                worksheet.write('B' + str(row), ', '.join(sorted(master[route][stop_id][route.direction0])),
                                text_wrap_format)
            else:
                worksheet.write('B' + str(row), '--', center_format)

            # Add second direction times
            if route.direction1 in master[route][stop_id]:
                worksheet.write('C' + str(row), ', '.join(sorted(master[route][stop_id][route.direction1])),
                                text_wrap_format)
            else:
                worksheet.write('C' + str(row), '--', center_format)
            row += 1

        # Close workbook
        workbook.close()
    return True


if __name__ == "__main__":
    publish()