from lxml import etree
import math

from src.scripts.constants import *
from src.scripts.web.constants import *
from src.scripts.web.tree_functions import *
from src.scripts.utils.IOutils import *


def add_time_table_body(stop_name, obj):
    tree = etree.Element('body')
    tree.append(add_class(etree.Element('div'), class_name="col-sm-12"))

    # Add stop title
    tree[0].append(add_stop_title(stop_name))
    etree.SubElement(tree[0], 'br')

    # Add route/directions columns
    for route_key in sorted(obj.keys()):
        tree.append(add_route_columns(route_key[0], obj[route_key]['directions'], len(obj), obj[route_key]))

    # Add footer
    etree.SubElement(tree, 'br')
    tree.append(add_time_table_footer())
    return tree


def add_stop_title(stop_name):
    tree = add_div(class_name="main")
    tree.text = stop_name
    return tree


def add_route_columns(route, directions, cols, obj):
    tree = add_div(class_name="col-sm-{}".format(math.floor((12 / cols) + 0.01)))
    tree.append(add_route_logo(route))
    tree.append(add_div(class_name="dirHeader route{}".format(route)))
    tree[1].text = 'to {}'.format(', '.join(directions))

    # Add column tables for each service text
    for service_text in obj:
        if service_text == 'directions':
            continue
        tree.append(add_column_table(service_text, obj[service_text]))
    return tree


def add_column_table(service_text, times):
    tree = add_div(class_name="table")

    # Add service text header
    tree.append(add_div(class_name="dayHeader"))
    tree[0].text = service_text

    # Add columns
    for time_column in times:
        tree.append(add_time_columns(time_column))
    etree.SubElement(tree, 'br')
    return tree


def add_time_columns(times):
    tree = add_div(class_name="col-md-6")
    i = 0
    for time in times:
        # Blank rows for the second column
        if not time:
            tree.append(add_div(class_name="entry"))
        # Afternoon/evening rows - add bold
        elif int(re.split(':', time)[0]) >= 12:
            tree.append(add_div(class_name="entry bold"))
            tree[i].text = time
        # Morning rows
        else:
            tree.append(add_div(class_name="entry"))
            tree[i].text = time
        i += 1
    return tree


def add_time_table_footer():
    tree = add_div(class_name="col-sm-12")
    tree.append(add_footer_image())
    tree.append(add_footer_text())
    return tree


def add_footer_image():
    tree = add_div(class_name="col-sm-12")
    tree.append(add_image(src="../../img/go_logo.jpg", id_name="footerImg"))
    return tree


def add_footer_text():
    tree = add_div(class_name="col-sm-12")
    tree.set('id', "footerText")

    # First line of footer
    tree.append(etree.Element('p'))
    tree[0].text = 'For questions or assistance planning your trip, please call the Transit Supervisor at \
                       (253) 966-3939.'

    # Second line of footer
    tree.append(etree.Element('p'))
    tree[1].append(etree.Element('span'))
    tree[1][0].text = 'All times are estimated for public guidance only. For real-time arrival estimates, use the \
                       OneBusAway app. '
    tree[1].append(etree.Element('em'))
    tree[1][1].text = 'GO'
    tree[1].append(etree.Element('span'))
    tree[1][2].text = ' Transit does not operate on Federal Holidays.'

    # Third line of footer
    tree.append(etree.Element('p'))
    tree[2].append(etree.Element('span'))
    tree[2][0].text = 'For current route maps and schedules please visit GOLewisMcChord.com. Like us on '
    tree[2].append(etree.Element('a', href="http://facebook.com/GOLewisMcChord"))
    tree[2][1].text = 'Facebook'
    tree[2].append(etree.Element('span'))
    tree[2][2].text = ' for current updates and news.'
    return tree


def publish_time_tables(time_table):
    # Establish report directory for time tables
    set_directory('{}/web/transit/stops'.format(REPORT_PATH))

    for stop in time_table:
        tree = etree.Element('html', lang='en')
        tree.append(add_head('GO Transit Timetable', css=[{'href': "../../css/go.css"},
                                                          {'href': "../../css/timetable.css"}]))
        tree.append(add_time_table_body(stop[1], time_table[stop]))

        writer = open('{}/web/transit/stops/{}.html'.format(REPORT_PATH, stop[0]), 'w')
        writer.write(string_with_doctype(tree).decode('utf-8'))