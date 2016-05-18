
import math
import os
import re
import shutil
import sys

# Entire scripts from src
import src.scripts.transit.route.route as rt
import src.scripts.transit.stop.stop as st
import src.scripts.transit.route.errors as RouteErrors

# Functions from src
from src.scripts.utils.functions import stack

# Variables from src
from src.scripts.transit.constants import PATH
from src.scripts.transit.route.constants import DISPLAY_ALL, TIMETABLE_HEADER, TIMETABLE_FOOTER, ORDER


class Stop(object):

    objects = {}

    def __init__(self, id, gps_ref):
        self.id = id
        self.obj = st.Stop.obj_map[id]
        self.gps_ref = gps_ref
        self.routes = {}

        Stop.objects[(id, gps_ref)] = self

    @staticmethod
    def get_stop(stop_id, gps_ref):
        if (stop_id, gps_ref) not in Stop.objects:
            Stop(stop_id, gps_ref)
        return Stop.objects[(stop_id, gps_ref)]

    def add_time(self, route, dirnum, dirname, schedule, time, joint):
        route = Route.get_route(self, route, dirnum)
        if dirname not in route.dirnames:
            route.dirnames.append(dirname)

        schedule = Schedule.get_schedule(self, route, schedule)
        schedule.times[time] = True
        if joint < schedule.joint:
            schedule.joint = joint

    def get_stop_html(self):
        return '\n\t\t<div class="main">\n\t\t\t{}\n\t\t</div></br>\n'.format(self.obj.name)


class Route(object):

    objects = {}

    def __init__(self, stop, route, dirnum):
        self.stop = stop  # Stop object
        self.route = route
        self.dirnum = dirnum
        self.dirnames = []
        self.schedules = {}
        self.order = {}

        stop.routes[(int(route.name[6:]), dirnum)] = self
        Route.objects[(stop, route, dirnum)] = self

    @staticmethod
    def get_route(stop, route, dirnum):
        if (stop, route, dirnum) not in Route.objects:
            Route(stop, route, dirnum)
        return Route.objects[(stop, route, dirnum)]

    def get_route_html(self, route_dirs=2):
        text = '\n\t<div class="col-md-{A}">\n\n\t\t\t<img src="../../img/route{B}_logo.jpg" class="imgHeader"/>\n\
                \n\t\t\t<div class="dirHeader route{B}">\n\t\t\t\tTO {C}\n\t\t\t</div>\n'.format(
                A=math.floor((12 / route_dirs) + 0.01), B=self.route.name[6:], C=', '.join(sorted(self.dirnames)))

        for schedule_order in sorted(self.order.keys()):
            text += self.order[schedule_order].get_schedule_html()

        return '{}\n\t\t</div>\n'.format(text)


class Schedule(object):

    objects = {}

    def __init__(self, stop, route, schedule):
        self.stop = stop  # Stop object
        self.route = route  # Route object
        self.schedule = schedule  # schedule text such as "Monday - Friday"
        self.joint = sys.maxsize
        self.times = {}

        route.schedules[self] = True
        try:
            route.order[ORDER[schedule]] = self
        except KeyError:
            route.order[sys.maxsize] = self
        Schedule.objects[(stop, route, schedule)] = self

    @staticmethod
    def get_schedule(stop, route, schedule):
        if (stop, route, schedule) not in Schedule.objects:
            Schedule(stop, route, schedule)
        return Schedule.objects[(stop, route, schedule)]

    def sort_times(self):
        """
        self.times = stack([rt.convert_to_24_time(time) for time in sorted(key[0:5] for key in self.times.keys())], 2,
                           'columns', 'columns')
        """
        self.times = stack([rt.convert_to_24_time(time) for time in sorted(key[0:5] for key in self.times.keys())], 2,
                           'columns', 'columns')
        return True

    def get_schedule_html(self):
        text = '\n\t\t\t<div class="table">\n\t\t\t\t<div class="dayHeader">\n\t\t\t\t\t{}\n\t\t\t\t</div>\n'.format(
            self.schedule)

        # text += '\n\t\t\t\t<div class="entry">\n\t\t\t\t\t{}\n\t\t\t\t</div>\n'.format(', '.join(self.times))

        for row in self.times:
            text += '\n\t\t\t\t<div class="col-md-6">\n'
            for entry in row:
                if not entry:
                    text += '\t\t\t\t\t<div class="entry"></div>\n'
                elif int(re.split(':', entry)[0]) >= 12:
                    text += '\t\t\t\t\t<div class="entry bold">{}</div>\n'.format(entry)
                else:
                    text += '\t\t\t\t\t<div class="entry">{}</div>\n'.format(entry)
            text += '\t\t\t\t</div>\n'

        return '{}\n\t\t\t</div></br>\n'.format(text)


def process():
    for obj in rt.StopTime.objects:
        stoptime = rt.StopTime.objects[obj]

        # Define terms
        display = stoptime.display
        stop = stoptime.stop_id
        gps_ref = stoptime.gps_ref
        stop_seq = stoptime.stop_seq
        trip = stoptime.trip
        route = stoptime.route
        dirnum = stoptime.trip.segment.sheet.dirnum
        dirname = stoptime.direction.name
        schedule = stoptime.trip.segment.service.text
        time = stoptime.depart_24p
        joint = int(stoptime.joint.id)

        # If the DISPLAY_ALL is set to False
        if not DISPLAY_ALL:
            # Remove objects who have a display value of 0
            if display == '0':
                continue

        # Remove destination values
        if stop_seq == sorted(trip.stop_times.keys())[-1]:
            continue

        # Find the appropriate Stop
        if (stop, gps_ref) not in Stop.objects:
            Stop(stop, gps_ref)
        stop = Stop.objects[(stop, gps_ref)]

        # Trickle information down to Route and Schedule objects
        stop.add_time(route, dirnum, dirname, schedule, time, joint)

    # Sort every schedule's times
    for obj in Schedule.objects:
        Schedule.objects[obj].sort_times()


def publish():
    # Establish report directory for timetables
    if not os.path.exists(PATH + '/reports/routes/timetables'):
        os.makedirs(PATH + '/reports/routes/timetables')

    # Process each stop's timetable
    for obj in Stop.objects:
        stop = Stop.objects[obj]

        writer = open('{}/reports/routes/timetables/{}{}.html'.format(PATH, stop.id, stop.gps_ref), 'w')

        writer.write(TIMETABLE_HEADER + stop.get_stop_html())

        for route in sorted(stop.routes.keys()):
            writer.write(stop.routes[route].get_route_html(len(stop.routes)))

        writer.write(TIMETABLE_FOOTER)
        writer.close()

        shutil.copyfile('{}/reports/routes/timetables/{}{}.html'.format(PATH, stop.id, stop.gps_ref),
                        '{}/reports/website/transit/stops/{}{}.html'.format(PATH, stop.id, stop.gps_ref))

    return True


if __name__ == "__main__":
    process()
    publish()
