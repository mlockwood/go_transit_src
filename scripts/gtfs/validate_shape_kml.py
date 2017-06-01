from pykml.factory import KML_ElementMaker as KML
from lxml import etree
from xml.sax.saxutils import unescape

from src.scripts.constants import *
from src.scripts.utils.IOutils import *


def validate():
    table = {}
    reader = open('{}/gtfs/files/shapes.txt'.format(REPORT_PATH))
    for line in reader:
        shape, lat, lng, seq = re.split(',', line.rstrip())
        if shape == 'shape_id':
            continue
        if shape not in table:
            table[shape] = {}
        table[shape][seq] = (lat, lng)

    # For each shape
    for shape in table:

        doc = KML.Document(KML.name('Shape {}'.format(shape)))

        # For each sequence in order
        for seq in sorted(table[shape].keys()):
            # Add a placemark in the KML file
            doc.append(KML.Placemark(
                KML.name('{}'.format(seq)),
                KML.styleUrl('#icon-503-777777'),
                KML.Point(
                    KML.coordinates('{},{},0'.format(table[shape][seq][1], table[shape][seq][0]))
                )
            ))

        # Add the normal style for the KML
        doc.append(KML.Style(
            KML.IconStyle(
                KML.color('ff777777'),
                KML.scale(1.1),
                KML.Icon(
                    KML.href('http://www.gstatic.com/mapspro/images/stock/503-wht-blank_maps.png')
                ),
                KML.hotspot('', x='16', y='31', xunits='pixels', yunits='insetPixels'),
            ),

            KML.LabelStyle(
                KML.scale(1.1)
            ),

            id='icon-503-777777-normal'))

        # Add the highlight style for the KML
        doc.append(KML.Style(
            KML.IconStyle(
                KML.color('ff555555'),
                KML.scale(1.1),
                KML.Icon(
                    KML.href('http://www.gstatic.com/mapspro/images/stock/503-wht-blank_maps.png')
                ),
                KML.hotSpot('', x='16', y='31', xunits='pixels', yunits='insetPixels'),
            ),

            KML.LabelStyle(
                KML.scale(1.1)
            ),

            id='icon-503-555555-highlight'))

        # Set the style map
        doc.append(KML.StyleMap(
            KML.Pair(
                KML.key('normal'),
                KML.styleUrl('#icon-503-777777-normal')
            ),

            KML.Pair(
                KML.key('highlight'),
                KML.styleUrl('#icon-503-777777-highlight')
            ),

            id='icon-503-777777'))

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
        set_directory('{}/gtfs/test'.format(REPORT_PATH))
        writer = open('{}/gtfs/test/shape_{}.kml'.format(REPORT_PATH, shape), 'w')
        writer.write('\n'.join(final))


if __name__ == "__main__":
    validate()



