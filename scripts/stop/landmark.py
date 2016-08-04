import csv
import re
import os
import src.scripts.stop.stop as st
from src.scripts.constants import PATH
from src.scripts.stop.constants import LANDMARK_HEADER


def process():
    points = [st.Point.objects[key] for key in sorted(st.Point.objects.keys())]

    matrix = [LANDMARK_HEADER]
    for point in points:
        if point.gps_n.lower() != 'unknown' and point.gps_w.lower() != 'unknown':
            matrix.append(['CREATE', '', '{}{}'.format(point.stop_id, point.gps_ref), 'bus',
                           '{} ({})'.format(point.name, point.gps_ref), st.convert_gps_dms_to_dd(point.gps_n),
                           st.convert_gps_dms_to_dd(point.gps_w), '', 100, 'F', 'Customer', 'Stop', 'YES', 'No', ''])

    if not os.path.exists(PATH + '/reports/stops/'):
        os.makedirs(PATH + '/reports/stops/')

    writer = csv.writer(open('{}/reports/stops/landmarks.csv'.format(PATH), 'w', newline=''), delimiter=',',
                        quotechar='|')

    for row in matrix:
        writer.writerow(row)

    return True


if __name__ == "__main__":
    process()
