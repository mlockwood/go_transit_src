import re
from lxml import etree
from xml.sax.saxutils import unescape
from pykml.factory import KML_ElementMaker as KML

from src.scripts.constants import *
from src.scripts.utils.IOutils import *


def get_cdata_html(route, service_text, start, end, directions, times):
    return '<h4>{} | {}-{}</h4><h5>Route {} to {}</h5>{}<hr>'.format(service_text, start.strftime('%H:%M'),
                                                                     end.strftime('%H:%M'), route, directions,
                                                                     ', '.join(times))


# Function to add style maps for changing the color of the buttons
def add_style(doc, color, highlight):

    # Add the normal style for the KML
    doc.append(KML.Style(
        KML.IconStyle(
            KML.color(color),
            KML.scale(1.1),
            KML.Icon(
                KML.href('http://www.gstatic.com/mapspro/images/stock/503-wht-blank_maps.png')
            ),
            KML.hotspot('', x='16', y='31', xunits='pixels', yunits='insetPixels'),
        ),

        KML.LabelStyle(
            KML.scale(1.1)
        ),

        id='icon-503-{}-normal'.format(color)))

    # Add the highlight style for the KML
    doc.append(KML.Style(
        KML.IconStyle(
            KML.color(highlight),
            KML.scale(1.1),
            KML.Icon(
                KML.href('http://www.gstatic.com/mapspro/images/stock/503-wht-blank_maps.png')
            ),
            KML.hotSpot('', x='16', y='31', xunits='pixels', yunits='insetPixels'),
        ),

        KML.LabelStyle(
            KML.scale(1.1)
        ),

        id='icon-503-{}-highlight'.format(highlight)))

    # Set the style map
    doc.append(KML.StyleMap(
        KML.Pair(
            KML.key('normal'),
            KML.styleUrl('#icon-503-{}-normal'.format(color))
        ),

        KML.Pair(
            KML.key('highlight'),
            KML.styleUrl('#icon-503-{}-highlight'.format(highlight))
        ),

        id='icon-503-{}'.format(color)))

    return doc


def publish_stop_kml(stop_table):
    doc = KML.Document(KML.name("GO Transit Stops"))

    # For each unique point of (stop, gps_ref)
    for stop in stop_table:

        cdata = '<![CDATA[<p>http://jblmmwr.com/golewismcchord/transit/stops/{}.html</p>'.format(stop[0])
        for key in sorted(stop_table[stop].keys()):
            cdata += get_cdata_html(*key, stop_table[stop][key])

        # Add a placemark in the KML file
        doc.append(KML.Placemark(
            KML.name('({}) {}'.format(stop[0], stop[1])),
            KML.description('{}]]>'.format(cdata)),
            KML.styleUrl('#icon-503-ff777777'),
            KML.Point(
                KML.coordinates('{},{},0'.format(stop[3], stop[2]))  # lng, lat here
            )
        ))

    doc = add_style(doc, 'ff777777', 'ff555555')
    doc = add_style(doc, 'ffA9445A', 'fff2dede')

    # Send KML file to string and replace spurious \
    kml = KML.kml(doc)
    kml = etree.tostring(kml, pretty_print=True).decode('utf-8', errors='strict').replace('\\', '')

    # Add encoding line
    final = ["<?xml version='1.0' encoding='UTF-8'?>"]

    # Unescape the CDATA description HTML
    for line in re.split('\n', kml):
        if re.search('\<description\>', line):
            final.append(unescape(line))
        else:
            final.append(line)

    # Write the file
    set_directory('{}/static/kml'.format(SRC_PATH))
    writer = open('{}/static/kml/stops.kml'.format(SRC_PATH), 'w')
    writer.write('\n'.join(final))



