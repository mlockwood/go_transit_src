import copy
import math
import re
import sys

from pykml import parser

import src.scripts.stop.stop as st
from src.scripts.constants import PATH


class Shape(object):

    objects = {}

    def __init__(self, name):
        self.name = name
        self.paths = {}
        self.nodes = {}
        self.distances = {}
        self.best = sys.maxsize
        self.order = []
        self.final_node = None
        self.index = 0
        self.origin = self.set_shape_node(st.Point.objects[(rt.Direction.objects[name].origin[:3],
                                                            rt.Direction.objects[name].origin[3:])])
        self.destination = self.set_shape_node(st.Point.objects[(rt.Direction.objects[name].destination[:3],
                                                                 rt.Direction.objects[name].destination[3:])])
        Shape.objects[name] = self

    def set_shape_node(self, node):
        new_node = Node(self, '', st.convert_gps_dms_to_dd(node.gps_n), st.convert_gps_dms_to_dd(node.gps_w))
        self.nodes[new_node] = True
        return new_node

    def add_path(self, points):
        self.paths[Path(self, points)] = True
        return True

    @staticmethod
    def haversine(x, y):
        if not isinstance(x, dict):
            raise TypeError('Haversine function\'s x parameter is not a dictionary.')
        if not isinstance(y, dict):
            raise TypeError('Haversine function\'s y parameter is not a dictionary.')

        # Set lat/lng for haversine
        lat = y['lat'] - x['lat']
        lng = y['lng'] - x['lng']

        # Calculate haversine
        a = math.sin(lat/2) ** 2 + math.cos(x['lat']) * math.cos(y['lat']) * math.sin(lng/2) ** 2
        c = 2 * math.asin(a ** 0.5)

        # Return haversine distance in kilometers
        return c * 6371

    def order_paths(self):
        for node in self.nodes:
            self.distances[node] = {}
            for to_node in [x for x in self.nodes.keys() if x != node and x.contra != node]:
                self.distances[node][to_node] = Shape.haversine(node.coords, to_node.coords)

        self.select_best_order(self.paths, self.origin, [], [])
        print(self.order)
        print('Shape {} had a final distance from the destination of {}\n\n'.format(self.name, Shape.haversine(
            self.final_node.coords, self.destination.coords)))
        return True

    def select_best_order(self, unseen, prev, order, reverse, distance=0):
        # Base case where there is only one unseen path
        if len(unseen) == 1:
            # If this order is less than any distance on record set as best
            path = [k for k in unseen.keys()][0]
            for node in path.nodes:
                if distance + self.distances[prev][node] < self.best:
                    self.best = distance + self.distances[prev][node]
                    self.final_node = node.contra
                    self.order = [x for x in zip(order+[path], reverse+[node.reverse])]


                # Otherwise use tiebreaking
                elif distance + self.distances[prev][node] == self.best:
                    if len(self.order[0][0].points) < len(order[0].points):
                        self.order = [x for x in zip(order+[path], reverse+[node.reverse])]

        # All other cases
        else:
            for path in unseen:
                for node in path.nodes:
                    if distance + self.distances[prev][node] < self.best:
                        new_unseen = copy.copy(unseen)
                        del new_unseen[path]
                        self.select_best_order(new_unseen, distance=distance+self.distances[prev][node],
                                               order=order+[path], reverse=reverse+[node.reverse], prev=node.contra)


class Path(object):

    def __init__(self, shape, points):
        self.shape = shape
        self.points = points
        print(shape.name, len(points))
        self.nodes = (Node(shape, self, points[0][1], points[0][0]),
                      Node(shape, self, points[-1][1], points[-1][0], reverse=True))
        self.nodes[0].contra = self.nodes[1]
        self.nodes[1].contra = self.nodes[0]

    def __repr__(self):
        return '<Path for {} with points ({}, {}) & ({}, {})>'.format(self.shape.name, self.points[0][1],
                                                                      self.points[0][0], self.points[-1][1],
                                                                      self.points[-1][0])

    def get_points(self, reverse):
        if reverse:
            return list(reversed(self.points))
        else:
            return self.points


class Node(object):

    def __init__(self, shape, path, lat, lng, reverse=False):
        self.shape = shape
        self.path = path
        self.lat = lat
        self.lng = lng
        self.reverse = reverse
        self.coords = self.convert_coord_to_dict()
        self.contra = None
        shape.nodes[self] = True

    def __repr__(self):
        return '<Node at {} {}>'.format(self.lat, self.lng)

    def convert_coord_to_dict(self):
        return {'lat': math.radians(float(self.lat)), 'lng': math.radians(float(self.lng))}


def process():
    shapes = [['shape_id', 'shape_pt_lat', 'shape_pt_lon', 'shape_pt_sequence']]
    # Open system.kml file in go/data/routes
    with open('{}/data/routes/system.kml'.format(PATH)) as file:
        doc = parser.parse(file)
        shape = None
        for t in doc.getiterator():

            # If the tag is a name, set name equal to the text contents of the name tag
            if re.sub('\{.*\}', '', t.tag).lower() == 'name':
                if t.text in rt.Direction.objects:
                    shape = Shape(t.text) if t.text not in Shape.objects else Shape.objects[t.text]
                else:
                    print('Shape {} did not process'.format(t.text))

            # Save coordinates
            if re.sub('\{.*\}', '', t.tag).lower() == 'coordinates':
                # A new Path must be created for the discovered coordinates
                shape.add_path([re.split(',', x) for x in re.split('\s', t.text) if len(re.split(',', x)) == 3])

    # Open writer
    writer = open('{}/reports/gtfs/files/shapes.txt'.format(PATH), 'w')
    writer.write('{}\n'.format(','.join(['shape_id', 'shape_pt_lat', 'shape_pt_lon', 'shape_pt_sequence'])))

    for obj in sorted(Shape.objects.keys()):
        shape = Shape.objects[obj]
        shape.order_paths()

        for path, reverse in shape.order:
            for point in path.get_points(reverse):
                writer.write('{}\n'.format(','.join([str(s) for s in [shape.name, point[1], point[0], shape.index]])))
                shape.index += 1

if __name__ == "__main__":
    process()

