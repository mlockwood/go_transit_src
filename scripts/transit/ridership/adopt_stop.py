import csv
import datetime
import math
import statistics
from src.scripts.transit.constants import PATH


stops = {}
records = {}


def add_record(date, stop, count):
    stops[stop] = []
    if date not in records:
        records[date] = {}
    records[date][stop] = records[date].get(stop, 0) + count
    return True


def get_stats(stop, start, end):
    counts = []
    dates = [start + datetime.timedelta(days=x) for x in range(0, (end - start).days + 1)]

    for date in dates:
        try:
            counts.append(records[date][stop])
        except KeyError:
            counts.append(0)

    return statistics.mean(counts), statistics.pstdev(counts)


def calc_nz_points(seed_avg, seed_stdev, adopt_avg):
    try:
        return math.ceil(math.log(adopt_avg - seed_avg + math.exp(1)) * (adopt_avg - seed_avg) / seed_stdev)
    except ZeroDivisionError:
        return math.ceil(math.log(adopt_avg - seed_avg + math.exp(1))) - 1
    except ValueError:
        return 0


def process(seed_start, seed_end, adopt_start, adopt_end):
    reader = csv.reader(open('{}/reports/ridership/records.csv'.format(PATH), 'r', newline=''), delimiter=',',
                        quotechar='|')

    for row in reader:
        if row[0].lower() == 'id':
            continue
        add_record(datetime.datetime(*[int(x) for x in row[1:4]]), row[-3], int(row[-1]))
        add_record(datetime.datetime(*[int(x) for x in row[1:4]]), row[-2], int(row[-1]))

    for stop in sorted(stops.keys()):
        nz = calc_nz_points(get_stats(stop, seed_start, seed_end)[0],
                            get_stats(stop, seed_start, seed_end)[1],
                            get_stats(stop, adopt_start, adopt_end)[0])
        stops[stop] = [get_stats(stop, seed_start, seed_end)[0], get_stats(stop, adopt_start, adopt_end)[0], nz]

        print(stop, stops[stop])

    return True

process(datetime.datetime(2015, 8, 31), datetime.datetime(2016, 1, 31), datetime.datetime(2016, 2, 1),
        datetime.datetime(2016, 5, 31))
