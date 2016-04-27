

import datetime
import math
import os
import re

# Entire scripts from src
import src.scripts.transit.route.route as rt
import src.scripts.transit.stop.stop as st
import src.scripts.transit.route.constants as RouteConstants
import src.scripts.transit.route.errors as RouteErrors

# Classes and variables from src
from src.scripts.transit.constants import PATH
from src.scripts.transit.route.constants import DISPLAY_ALL, SCHEDULE_TEXT


class Route(object):

    objects = {}

    def __init__(self, route):
        self.id = route.id
        self.name = route.name
        self.route = route
        self.schedules = {}
        Route.objects[route.id] = self

    def print_schedules(self):
        print('\n\n{}'.format(self.name))
        for schedule in sorted(self.schedules.keys()):
            print('TO {}'.format(' & '.join(self.schedules[schedule].dirnames)))
            for stop in Stop.seq_sorted(self.schedules[schedule].stops):
                print('\t', stop.stop, stop.times)
            print('\n')

    def get_logo_html(self):
        return '\n\t<div>\n\t\t<img src="img/route{}_logo.jpg" class="imgHeader"/>\n\t</div>\n'.format(self.name[6:])

    def get_map_html(self):
        return '\n\t<div>\n\t\t<embed src="img/route{}_map.pdf" width="1680" height="700" type=application/pdf>\n\
        \t</div>\n'.format(self.name[6:])


class Schedule(object):

    objects = {}

    def __init__(self, route, joint, dirnum):
        self.joint = joint
        self.dirnum = dirnum
        self.origins = {}
        self.dirnames = []
        self.stops = {}

        Schedule.objects[(route.id, joint.id, dirnum)] = self

        if route.id not in Route.objects:
            Route(route)
        self.route = Route.objects[route.id]
        self.route.schedules[(joint.id, dirnum)] = self

    def make(self):
        # Figure out the number of trips there should be
        count = round((self.joint.end_time - self.joint.start_time).total_seconds() / self.joint.headway)

        # If the route operates less than two hours list all of the times
        if (self.joint.end_time - self.joint.start_time).total_seconds() < 7200 or count < 6:
            for stop in self.stops:
                stop.convert_to_list()

        # For routes that have a headway that is equally divisible into hour sections
        elif 3600 % self.joint.headway == 0:

            # Iterate through each stop to determine if the stop qualifies
            for stop in self.stops:

                # If the headway timing test passes, convert to xx:00 time
                if stop.test_timing_headways():
                    stop.convert_to_xx()

                # Else move to the exceptions dict for the Route
                else:
                    stop.convert_to_list()

        # For routes that do not have an equally divisible headway
        else:
            # Sort the times of schedules that cannot have xx:00
            for stop in self.stops:
                stop.convert_to_list()

        return True

    def get_schedule_header_html(self):
        return '\n\t<div class="col-md-12 scheduleHeader">\n\t\t{}</br>\n\t\t{} - {}\n\t</div>\n'.format(
            self.joint.schedule_text, self.joint.start_time.strftime('%H:%M'), self.joint.end_time.strftime('%H:%M'))

    def get_schedule_html(self, dirs=2):
        text = '\n\t<div class="col-md-{}">\n\n\t\t<div class="col-md-12 directionHeader route{}">\n\t\t\t{} to {}\n\
               \t\t</div></br>\n'.format(math.floor((12 / dirs) + 0.01), self.route.name[6:],
                                         ', '.join(self.origins.keys()), ', '.join(self.dirnames))
        for stop in Stop.seq_sorted(self.stops):
            text += stop.get_stop_html()

        return text + '\n\t</div>'


class Stop(object):

    objects = {}

    def __init__(self, route, schedule, stop, stop_seq):
        self.route = route
        self.schedule = schedule
        self.stop = stop
        self.stop_seq = stop_seq
        self.times = {}

        Stop.objects[(schedule, stop)] = self

    @staticmethod
    def seq_sorted(stop_dict):
        keys = sorted([(stop.stop_seq, stop) for stop in stop_dict])
        return [stop[1] for stop in keys]

    def add_time(self, time):
        self.times[time] = True
        return True

    def convert_to_list(self):
        self.times = sorted(key[0:5] for key in self.times.keys())
        return True

    def test_timing_headways(self):
        # Collect stop times and set the first one to the prev key
        test = True
        times = sorted(self.times.keys())
        prev = datetime.datetime.strptime(times[0], '%H:%M:%S')

        # Iterate through the keys and check that each progression is exactly a headway apart
        for time in times[1:]:
            prev += datetime.timedelta(seconds=self.schedule.joint.headway)
            if datetime.datetime.strptime(time, '%H:%M:%S') != prev:
                test = False

        return test

    def convert_to_xx(self):
        new_times = {}
        for time in self.times:
            new_times['xx:{}'.format(time[3:5])] = True
        self.times = sorted(new_times.keys())
        return True

    def get_stop_html(self):
        return '\n\t\t<div class="col-md-12">\n\t\t\t<div class="col-md-1">\n\t\t\t\t<div class="stopCircle">\n\
        \t\t\t\t\t{}\n\t\t\t\t</div>\n\t\t\t</div>\n\t\t\t<div class="col-md-4 stopInfo">\n\t\t\t\t{}\n\t\t\t</div>\n\
        \t\t\t<div class="col-md-7 stopInfo">\n\t\t\t\t{}\n\t\t\t</div>\n\t\t</div>\n\
        '.format(self.stop, st.Stop.obj_map[self.stop].name, ', '.join(self.times))


def process():
    # Add StopTime object values to the correct DS
    for obj in rt.StopTime.objects:
        stoptime = rt.StopTime.objects[obj]

        # If the DISPLAY_ALL is set to False
        if not DISPLAY_ALL:
            # Remove objects who have a display value of 0
            if stoptime.display == '0':
                continue

        # Define terms
        route = stoptime.route
        joint = stoptime.joint
        dirnum = stoptime.trip.segment.sheet.dirnum
        dirname = stoptime.direction.name
        stop = stoptime.stop_id
        stop_seq = stoptime.stop_seq
        time = stoptime.depart

        if not joint:
            continue

        # Find the appropriate Schedule
        if (route.id, joint.id, dirnum) not in Schedule.objects:
            Schedule(route, joint, dirnum)
        schedule = Schedule.objects[(route.id, joint.id, dirnum)]

        # Add the stoptime values to the Schedule
        if dirname not in schedule.dirnames:
            schedule.dirnames.append(dirname)

        # Find the appropriate Stop
        if (schedule, stop) not in Stop.objects:
            Stop(schedule.route, schedule, stop, stop_seq)
        stop = Stop.objects[(schedule, stop)]

        # Select the largest stop_seq
        if stop_seq > stop.stop_seq:
            stop.stop_seq = stop_seq

        # Add stop_seq of 1 so the origin
        if stop_seq == 1:
            schedule.origins[st.Stop.obj_map[stop.stop].name] = True

        # Add the current time to the stop and then add the stop to the schedule
        stop.add_time(time)
        schedule.stops[stop] = True

    for obj in Schedule.objects:
        schedule = Schedule.objects[obj]
        schedule.make()

    return True


def publish():
    for obj in Route.objects:
        route = Route.objects[obj]

        # Establish report directory for schedules
        if not os.path.exists(PATH + '/reports/routes/schedules/'):
            os.makedirs(PATH + '/reports/routes/schedules/')

        writer = open('{}/reports/routes/schedules/{}.html'.format(PATH, re.sub(' ', '', route.name)), 'w')
        writer.write(SCHEDULE_TEXT + route.get_logo_html() + route.get_map_html())

        observed = {}
        for schedule in sorted(route.schedules):
            if schedule[0] not in observed:
                writer.write(route.schedules[schedule].get_schedule_header_html())
                observed[schedule[0]] = True
            writer.write(route.schedules[schedule].get_schedule_html())

        writer.write('\n</body>\n</html>')


if __name__ == "__main__":
    process()
    publish()