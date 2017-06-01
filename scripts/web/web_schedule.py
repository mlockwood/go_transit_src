# Import scripts from src
from src.scripts.route.route import *
from src.scripts.web.constants import ROUTE_SCRIPT
from src.scripts.web.tree_functions import *
from src.scripts.utils.IOutils import *


def add_schedule_body(route, joints):
    tree = etree.Element('body')
    tree.append(add_route_logo(route))
    tree.append(add_div(class_name="col-md-12"))
    tree[1].append(add_div(id_name="map"))
    i = 2
    for joint in joints:
        # Add joint
        tree.append(add_schedule_header(joints[joint]['service_text'], joints[joint]['start'], joints[joint]['end']))
        i += 1

        # Add each segment
        for order in sorted(joints[joint]['segments'].keys()):
            obj = joints[joint]['segments'][order]
            tree.append(add_segment_header(route, obj['origins'], obj['directions'],
                                           dirs=len(joints[joint]['segments'])))

            # Add stops for each segment
            del obj['origins']
            del obj['directions']
            for stop in sorted(obj.keys()):
                tree[i].append(add_stop_entry(**obj[stop]))
            i += 1

    # Add map scripts
    tree.append(etree.Element('script', src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.4/jquery.min.js"))
    tree.append(add_map_scripts(route))
    tree.append(etree.Element('script',
        src="https://maps.googleapis.com/maps/api/js?key=AIzaSyCgsmKLx0UBD6zwRT0P4WGuimjZ1KR5eR8&callback=initialize"))
    return tree


def add_schedule_header(service_text, start, end):
    tree = add_div(class_name="col-md-12 scheduleHeader")
    tree.text = service_text
    br = etree.SubElement(tree, 'br')
    br.tail = '{} - {}'.format(start.strftime('%H:%M'), end.strftime('%H:%M'))
    return tree


def add_segment_header(route, origins, directions, dirs=2):
    tree = add_div(class_name="col-md-{}".format(math.floor((12 / dirs) + 0.01)))
    tree.append(add_div(class_name="col-md-12 directionHeader route{}".format(route)))
    tree[0].text = '{} to {}'.format(', '.join(list(origins.keys())), ', '.join(list(directions.keys())))
    etree.SubElement(tree, 'br')
    return tree


def add_stop_entry(id, loc, gps_ref, name, times):
    tree = add_div(class_name="col-md-12")
    tree.append(add_div(class_name="col-md-1"))
    tree[0].append(add_div(class_name="stopCircle"))
    tree[0][0].text = loc
    tree.append(etree.Element('a', href="../stops/{}.html".format(id)))
    tree[1].append(add_div(class_name="col-md-4 stopInfo"))
    tree[1][0].text = '{} ({})'.format(name, gps_ref)
    tree.append(add_div(class_name="col-md-7 stopInfo"))
    tree[2].text = ', '.join(times)
    return tree


def add_map_scripts(route):
    tree = etree.Element('script')
    tree.text = ROUTE_SCRIPT.format(route)
    return tree


def publish_schedules(web_schedule):
    # Establish report directory for schedules
    set_directory('{}/web/transit/routes'.format(REPORT_PATH))

    for route in web_schedule:
        tree = etree.Element('html', lang='en')
        tree.append(add_head('GO Transit Schedule', css=[{'href': "../../css/go.css"},
                                                         {'href': "../../css/schedule.css"}]))
        tree.append(add_schedule_body(route, web_schedule[route]))

        writer = open('{}/web/transit/routes/route{}.html'.format(REPORT_PATH, route), 'w')
        writer.write(string_with_doctype(tree).decode('utf-8'))