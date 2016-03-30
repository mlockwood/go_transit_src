import csv
import datetime
import re


version_1 = datetime.date(2015, 8, 31)
version_2 = datetime.date(2015, 9, 8)
version_3 = datetime.date(2015, 10, 30)


chars = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T']
header = ['Boarding', 'Time', 'Count', 'Destination']

def load_version(version):
    reader = csv.reader(open('version{}.csv'.format(str(version)), 'r', newline=''), delimiter=',', quotechar='|')
    standard_bool = False
    meta_map_bool = False
    standard = {}
    meta_map = {}
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
            standard[row[0]] = row[1]

        elif meta_map_bool:
            meta_map[row[0]] = row[1]

    return standard, meta_map

standard, meta_map = load_version(3)