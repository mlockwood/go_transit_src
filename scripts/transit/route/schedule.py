

import datetime
import math
import os
import re

# Entire scripts from src
import src.scripts.transit.route.route as rt
import src.scripts.transit.stop.stop as st
import src.scripts.transit.route.errors as RouteErrors

# Classes and variables from src
from src.scripts.transit.constants import PATH
from src.scripts.transit.route.constants import DISPLAY_ALL, SCHEDULE_HEADER


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

    def get_schedule_html(self, dirs=2, civic_plus=False):
        text = '\n\t<div class="col-md-{}">\n\n\t\t<div class="col-md-12 directionHeader route{}">\n\t\t\t{} to {}\n\
               \t\t</div></br>\n'.format(math.floor((12 / dirs) + 0.01), self.route.name[6:],
                                         ', '.join(self.origins.keys()), ', '.join(self.dirnames))
        for stop in Stop.seq_sorted(self.stops):
            if civic_plus:
                text += stop.get_stop_html_for_civic_plus()
            else:
                text += stop.get_stop_html()

        return text + '\n\t</div>'


class Stop(object):

    objects = {}

    def __init__(self, route, schedule, stop, stop_seq, gps_ref=None):
        self.route = route
        self.schedule = schedule
        self.stop = stop
        self.stop_seq = stop_seq
        self.gps_ref = gps_ref
        self.times = {}

        Stop.objects[(schedule, stop, gps_ref)] = self

    @staticmethod
    def objects_sorted():
        keys = sorted([(obj[1], obj[2], obj[0].joint.id, obj[0].dirnum, obj[0].route.id, Stop.objects[obj])
                       for obj in Stop.objects.keys() if obj[2]])
        return [stop[-1] for stop in keys]

    @staticmethod
    def seq_sorted(stop_dict):
        keys = sorted([(stop.stop_seq, stop) for stop in stop_dict if not stop.gps_ref])
        return [stop[1] for stop in keys]

    def add_time(self, time):
        self.times[time] = True
        return True

    def convert_to_list(self):
        self.times = [rt.convert_to_24_time(time) for time in sorted(key[0:5] for key in self.times.keys())]
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

    def get_stop_html_for_civic_plus(self):
        return '\n\t\t<div class="col-md-12">\n\t\t\t<div class="col-md-2">\n\t\t\t\t<div class="stopCircle">\n\
        \t\t\t\t\t{}\n\t\t\t\t</div>\n\t\t\t</div>\n\t\t\t<div class="col-md-4 stopInfo">\n\t\t\t\t{}\n\t\t\t</div>\n\
        \t\t\t<div class="col-md-6 stopInfo">\n\t\t\t\t{}\n\t\t\t</div>\n\t\t</div>\n\
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
        gps_ref = stoptime.gps_ref
        stop_seq = stoptime.order
        time = stoptime.depart_24p

        # Find the appropriate Schedule
        if (route.id, joint.id, dirnum) not in Schedule.objects:
            Schedule(route, joint, dirnum)
        schedule = Schedule.objects[(route.id, joint.id, dirnum)]

        # Add the stoptime values to the Schedule
        if dirname not in schedule.dirnames:
            schedule.dirnames.append(dirname)

        # Find the appropriate Point
        if (schedule, stop, gps_ref) not in Stop.objects:
            Stop(schedule.route, schedule, stop, stop_seq, gps_ref)
        point = Stop.objects[(schedule, stop, gps_ref)]

        # Find the appropriate Stop
        if (schedule, stop, None) not in Stop.objects:
            Stop(schedule.route, schedule, stop, stop_seq)
        stop = Stop.objects[(schedule, stop, None)]

        # Select the largest stop_seq
        if stop_seq > stop.stop_seq:
            stop.stop_seq = stop_seq
            point.stop_seq = stop_seq

        # Add stop_seq of 1 so the origin
        if stop_seq == 1:
            schedule.origins[st.Stop.obj_map[stop.stop].name] = True

        # Add the current time to the stop and then add the stop to the schedule
        stop.add_time(time)
        point.add_time(time)
        schedule.stops[stop] = True
        schedule.stops[point] = True

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
        writer.write(SCHEDULE_HEADER + route.get_logo_html() + route.get_map_html())

        observed = {}
        joint = {}
        for schedule in route.schedules:
            joint[route.schedules[schedule].joint] = joint.get(route.schedules[schedule].joint, 0) + 1

        for schedule in sorted(route.schedules):
            if schedule[0] not in observed:
                writer.write(route.schedules[schedule].get_schedule_header_html())
                observed[schedule[0]] = True
            writer.write(route.schedules[schedule].get_schedule_html(dirs=joint[route.schedules[schedule].joint],
                         civic_plus=True))

        writer.write('\n</body>\n</html>')


def stop_schedule():
    table = {}

    # Process if not __name__ == "__main__"
    if __name__ != "__main__":
        process()

    prev = None
    # Add StopTime object values to the correct DS
    for point in Stop.objects_sorted():

        # Define terms
        stop = point.stop
        gps_ref = point.gps_ref
        schedule = point.schedule
        route = point.route

        if (stop, gps_ref, schedule) == prev:
            table[(stop, gps_ref)] = table.get((stop, gps_ref), '') + (
                '<h5> Route {D} to {E} </h5>{F}<hr>'.format(
                    D=route.id,
                    E=', '.join(schedule.dirnames),
                    F=', '.join(Stop.objects[(schedule, stop, gps_ref)].times)
                )
            )

        else:
            table[(stop, gps_ref)] = table.get((stop, gps_ref), '') + (
                '<h4>{A} | {B}-{C}</h4><h5> Route {D} to {E} </h5>{F}<hr>'.format(
                    A=schedule.joint.schedule_text,
                    B=schedule.joint.start_time.strftime('%H:%M'),
                    C=schedule.joint.end_time.strftime('%H:%M'),
                    D=route.id,
                    E=', '.join(schedule.dirnames),
                    F=', '.join(Stop.objects[(schedule, stop, gps_ref)].times)
                )
            )

        prev = (stop, gps_ref, schedule)

    return table

if __name__ == "__main__":
    process()
    publish()