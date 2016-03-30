
import os
import re

"""
GO Imports-------------------------------------------------------------
"""
import src.scripts.transit.constants as System
import src.scripts.transit.route.route as rt
import src.scripts.transit.stop.stop as st

"""
Main -------------------------------------------------------------------
"""
base = ('<!doctype html>\n' +
        '<!--[if lt IE 7]> <html class="lt-ie9 lt-ie8 lt-ie7" lang="en"> <![endif]-->\n' +
        '<!--[if IE 7]> <html class="lt-ie9 lt-ie8" lang="en"> <![endif]-->\n' +
        '<!--[if IE 8]> <html class="lt-ie9" lang="en"> <![endif]-->\n' +
        '<!--[if gt IE 8]><!--> <html lang="en"> <!--<![endif]-->\n' +
        '<head>\n' +
        '\t<title>GO TRANSIT TIMETABLE</title>\n' +
        '\t<link rel="stylesheet" href="css/go.css">\n' +
        '</head>\n<body>\n')


def build_master_table():
    master_table = {}
    dir_table = {}
    for ST in rt.StopTime.objects:
        obj = rt.StopTime.objects[ST]

        # Set master table value [stop][gps_ref][route][time]
        if obj.stop_id not in master_table:
            master_table[obj.stop_id] = {}
        if obj.gps_ref not in master_table[obj.stop_id]:
            master_table[obj.stop_id][obj.gps_ref] = {}
        if obj.route.name not in master_table[obj.stop_id][obj.gps_ref]:
            master_table[obj.stop_id][obj.gps_ref][obj.route.name] = []
        master_table[obj.stop_id][obj.gps_ref][obj.route.name].append(
            obj.time)

        # Set dir table value
        dir_table[(obj.stop_id, obj.gps_ref, obj.route.name)] = obj.direction
    return master_table, dir_table


def publish():
    # Establish report directory for timetables
    if not os.path.exists(System.path + '/reports/routes/timetables'):
        os.makedirs(System.path + '/reports/routes/timetables')

    # Build the input tables
    master, dir_table = build_master_table()

    # Iterate through each stop
    for stop in sorted(master.keys()):
        if not stop:
            continue

        # Build a timetable for each sign at the stop (by gps_ref)
        for ref in sorted(master[stop].keys()):
            # Add html document information
            doc = (base + '\t<div id="stop">' + eval('st.Stop.obj_map[stop' +
                                                     '].name') +
                   '</div>\n\t<div class="main">\n')
            # Review each route at the stop ref
            for route in sorted(master[stop][ref].keys()):
                # Route name
                route_name = re.sub(' ', '', route.lower())
                route_number = route_name[5:]

                # Find stop direction for stop, ref, route
                direction = dir_table[(stop, ref, route)]
                if direction == 'Pendleton Shoppette':
                    direction = 'Pend. Shoppette'
                elif direction == 'Joint Base Headquarters':
                    direction = 'Joint Base HQ'

                # Find service days
                days = rt.Route.objects[route].service_text

                # Add basic route information and headers
                doc += ('\t\t<div class="route">\n' +
                        '\t\t\t<img src="img/{}_logo.jpg" class="imgHeader" />\n'.format(route_name) +
                        '\t\t\t<div class="dirHeader" id="{}">TO {}</div>\n'.format(route_name, direction.name) +
                        '\t\t\t<div class="table">\n' +
                        '\t\t\t\t<div class="dayHeader">{}</div>\n'.format(days) +
                        '\t\t\t\t<div class="column">\n')

                # Add time entries
                i = 0
                times = sorted(master[stop][ref][route])
                while i < 40:
                    # Cap columns at twenty entries
                    if i == 20:
                        doc += ('\t\t\t\t</div>\n' +
                                '\t\t\t\t<div class="column">\n')
                    if i < len(times):
                        # If the entry is 12:00 or later, make it bold
                        if int(times[i][0:2]) >= 12:
                            doc += ('\t\t\t\t\t<div class="entry bold">' +
                                    times[i] + '</div>\n')
                        # Otherwise do not bold it
                        else:
                            doc += ('\t\t\t\t\t<div class="entry">' +
                                    times[i] + '</div>\n')
                    # Handle empty entries
                    else:
                        doc += '\t\t\t\t\t<div class="entry"></div>\n'
                    i += 1

                # Close route divs
                doc += '\t\t\t\t</div>\n\t\t\t</div>\n\t\t</div>\n'

            # Add footer
            doc += ('\t<div id="footer">\n' +
                    '\t\t<div id="footerText">\n' +
                    '\t\t\t<p>For questions or assistance planning your ' +
                    'trip, please call the Transit Supervisor at (253) ' +
                    '966-3939.</p>\n' +
                    '\t\t\t<p>All times are estimated for public ' +
                    'guidance only. GO Transit does not operate on ' +
                    'Federal Holidays.</p>\n' +
                    '\t\t\t<p>For current route maps and schedules ' +
                    'please visit www.facebook.com/GoLewisMcChord.</p>\n' +
                    '\t\t</div>\n' +
                    '\t\t<img src="img/go_logo.jpg" ' +
                    'id="footerImg" />\n' +
                    '\t</div>\n' +
                    '</body>\n' +
                    '</html>\n')

            # Write document
            writer = open(System.path + '/reports/routes/timetables/' +
                          re.sub(' |\-', '_', stop) + str(ref) + '.html', 'w')
            writer.write(doc)
    return True

if __name__ == "__main__":
    publish()
