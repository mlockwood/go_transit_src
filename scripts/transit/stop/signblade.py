import os
import re
import xlsxwriter

# Entire scripts from src
import src.scripts.transit.route.route as rt
import src.scripts.transit.stop.stop as st

# Classes and variables from src
from src.scripts.constants import PATH


def build_stop_table():
    stops = {}

    # Add StopTime object values to the correct DS
    for obj in rt.StopTime.objects:
        stoptime = rt.StopTime.objects[obj]

        # Define terms
        stop_id = stoptime.stop_id
        gps_ref = stoptime.gps_ref
        stop_seq = stoptime.stop_seq
        trip = stoptime.trip
        route = stoptime.route.name[6:]
        dirname = stoptime.direction.name

        # Remove destination values
        if stop_seq == sorted(trip.stop_times.keys())[-1]:
            if len(stoptime.route.dirnums) > 1:
                continue

        # Set stops[(stop_id, gps_ref)][route_name][direction_name] = True
        if (stop_id, gps_ref) not in stops:
            stops[(stop_id, gps_ref)] = {}
        if route not in stops[(stop_id, gps_ref)]:
            stops[(stop_id, gps_ref)][route] = {}
        stops[(stop_id, gps_ref)][route][dirname] = True

    return stops


def build_stop_templates(stops):
    templates = {}

    for stop in stops:
        routes = tuple(sorted([int(key) for key in stops[stop].keys()]))
        dirnames = []
        for route in sorted([int(key) for key in stops[stop].keys()]):
            dirnames.append('({})-{}'.format(str(route), ', '.join(sorted(stops[stop][str(route)]))))

        if routes not in templates:
            templates[routes] = {}
        if tuple(dirnames) not in templates[routes]:
            templates[routes][tuple(dirnames)] = {}
        templates[routes][tuple(dirnames)][stop] = True

    return templates


def publish():
    if not os.path.exists(PATH + '/reports/stops/'):
        os.makedirs(PATH + '/reports/stops/')

    # Build the stop table
    stops = build_stop_table()

    # Open workbook and worksheet
    workbook = xlsxwriter.Workbook('{}/reports/stops/signblades.xlsx'.format(PATH))
    worksheet = workbook.add_worksheet('signblades')

    # Set column widths
    worksheet.set_column('A:A', 4)
    worksheet.set_column('B:B', 16)
    worksheet.set_column('C:C', 40)

    # Format declarations
    merge_format = workbook.add_format({'font_size': '20',
                                        'bold': True,
                                        'fg_color': '#D7E4BC',
                                        #  'align': 'center',
                                        })

    # Write data
    row = 1
    for (stop, gps_ref) in sorted(stops.keys()):
        # Set stop information row
        worksheet.merge_range('A{n}:C{n}'.format(n=row), '{} {} | REF: {}'.format(stop, st.Stop.obj_map[stop].name,
                                                                                  gps_ref), merge_format)
        row += 1

        # Set route, direction pairs for the stop
        for route in sorted([int(key) for key in stops[(stop, gps_ref)].keys()]):
            dirnames = ', '.join(sorted(stops[(stop, gps_ref)][str(route)].keys()))
            worksheet.write_row('B{}'.format(row), ['Route {}'.format(str(route)), dirnames])
            row += 1

        row += 1

    # Close workbook
    workbook.close()

    # Build template version for configuring which template to build the sign from
    templates = build_stop_templates(stops)

    # Open workbook and worksheet
    workbook = xlsxwriter.Workbook('{}/reports/stops/signblade_templates.xlsx'.format(PATH))
    worksheet = workbook.add_worksheet('signblades')

    # Set column widths
    worksheet.set_column('A:A', 4)
    worksheet.set_column('B:B', 4)
    worksheet.set_column('C:C', 40)

    # Format declarations
    merge_format = workbook.add_format({'font_size': '20',
                                        'bold': True,
                                        'fg_color': '#D7E4BC',
                                        #  'align': 'center',
                                        })

    # Write data
    row = 1
    for route in sorted(templates.keys()):
        # Set route template row
        worksheet.merge_range('A{n}:C{n}'.format(n=row), 'Routes {}'.format('-'.join(str(s) for s in route)),
                              merge_format)
        row += 1

        # Set route-direction template row
        for route_dir in sorted(templates[route].keys()):
            worksheet.merge_range('B{n}:C{n}'.format(n=row), ' | '.join(route_dir))
            row += 1

            for stop in sorted(templates[route][route_dir].keys()):
                worksheet.write_row('C{}'.format(row), ['{}{} - {}'.format(stop[0], stop[1],
                                                                           st.Stop.obj_map[stop[0]].name)])
                row += 1

        row += 1

    # Close workbook
    workbook.close()

    return True


if __name__ == "__main__":
    publish()


