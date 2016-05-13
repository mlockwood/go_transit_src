import csv
import datetime
import re


VERSION1 = datetime.date(2015, 8, 31)
VERSION2 = datetime.date(2015, 9, 8)
VERSION3 = datetime.date(2015, 10, 30)
CHARS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T']
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