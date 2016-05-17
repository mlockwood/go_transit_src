import copy
import re
import sys

from pykml.factory import KML_ElementMaker as KML
from pykml.factory import GX_ElementMaker as GX
from lxml import etree

import src.scripts.transit.stop.stop as st
from src.scripts.transit.constants import PATH

doc = KML.Document(KML.name("GO Transit Stops"))

for obj in st.Point.objects:
    stop = st.Point.objects[obj]
    if st.convert_gps_dms_to_dd(stop.gps_n) and st.convert_gps_dms_to_dd(stop.gps_w) and stop.available == '1':
        doc.append(KML.Placemark(
            KML.name(stop.name),
            KML.description(stop.desc + ' TEST'),
            KML.Point(
                KML.coordinates('{},{},0'.format(st.convert_gps_dms_to_dd(stop.gps_w),
                                                 st.convert_gps_dms_to_dd(stop.gps_n)))
            )
        ))

kml = KML.kml(doc)
kml = re.sub('\&amp;', '&', etree.tostring(kml, pretty_print=True).decode('utf-8', errors='strict')).replace('\\', '')

writer = open('{}/reports/stops/stops.kml'.format(PATH), 'w')
writer.write(kml)



