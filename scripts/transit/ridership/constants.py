import csv
import datetime
import re


VERSION1 = datetime.datetime(2015, 8, 31)
VERSION2 = datetime.datetime(2015, 9, 8)
VERSION3 = datetime.datetime(2015, 10, 30)
CHARS = list(map(chr, range(65, 91)))
HEADER = ['Boarding', 'Time', 'Count', 'Destination']


def load_version(version):
    reader = csv.reader(open('version{}.csv'.format(str(version)), 'r', newline=''), delimiter=',', quotechar='|')
    standard_bool = False
    meta_map_bool = False
    standard = {}
    order = {}
    meta_map = {}
    i = 0
    for row in reader:
        if not re.sub(' ', '', ''.join(row)):
            continue

        if row[0] == 'STANDARD':
            standard_bool = True
            meta_map_bool = False

        elif row[0] == 'META_MAP':
            standard_bool = False
            meta_map_bool = True

        elif standard_bool:
            standard[row[0]] = (row[1], row[2])
            order[i] = row[0]
            i += 1

        elif meta_map_bool:
            meta_map[row[0]] = row[1]

    return standard, order, meta_map

STANDARD, ORDER, META_MAP = load_version(3)