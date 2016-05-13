import copy
import re
import sys

from pykml import parser

from src.scripts.transit.constants import PATH


class Shape(object):

    objects = {}

    def __init__(self, name):
        self.name = name
        self.paths = {}
        self.distances = {}
        self.best = sys.maxsize
        self.order = []
        self.index = 0
        Shape.objects[name] = self

    def add_path(self, coords):
        self.paths[Path(self, Path.convert_coord_to_dict(coords[0]), Path.convert_coord_to_dict(coords[-1]),
                        coords)] = True
        return True

    def order_paths(self):
        # No need to order if there is only one path
        if len(self.paths) == 1:
            self.order = [k for k in self.paths.keys()]
            return True

        for path in self.paths:
            self.distances[path] = {}
            for to_path in [x for x in self.paths.keys() if x != path]:
                self.distances[path][to_path] = Shape.euclidean(path.destination, to_path.origin)
        
        self.select_best_order(self.paths)
        return True

    @staticmethod
    def euclidean(x, y):
        if not isinstance(x, dict):
            raise TypeError('Euclidean function\'s x parameter is not a dictionary.')
        if not isinstance(y, dict):
            raise TypeError('Euclidean function\'s y parameter is not a dictionary.')

        # Calculate euclidean distance by add the squared distance of all matched dimensions and the squared distance
        # away from the origin in mismatched dimensions.
        distance = 0
        for d in x:
            if d in y:
                distance += (float(x[d]) - float(y[d])) ** 2
            else:
                distance += float(x[d]) ** 2
        for d in [d for d in y.keys() if d not in x]:
            distance += float(y[d]) ** 2

        return distance ** 0.5

    def select_best_order(self, unseen, order=[], distance=0, prev=None):
        # Base case where there is only one unseen path
        if len(unseen) == 1:
            # If this order is less than any distance on record set as best
            key = [k for k in unseen.keys()][0]
            if distance + self.distances[prev][key] < self.best:
                self.best = distance + self.distances[prev][key]
                self.order = order

            # Otherwise use tiebreaking
            elif distance + self.distances[prev][key] == self.best:
                if self.order[0].coords < order[0].coords:
                    self.order = order

        # Case where no processing has begun, init by starting to recurse each path combination
        elif not prev:
            for path in unseen:
                new_unseen = copy.copy(unseen)
                del new_unseen[path]
                return self.select_best_order(new_unseen, order=[path], prev=path)

        # All other cases
        else:
            for path in unseen:
                if distance + self.distances[prev][path] < self.best:
                    new_unseen = copy.copy(unseen)
                    del new_unseen[path]
                    return self.select_best_order(new_unseen, distance=distance+self.distances[prev][path],
                                                  order=order+[path], prev=path)

        return True


class Path(object):

    def __init__(self, shape, origin, destination, coords):
        self.shape = shape
        self.origin = origin if isinstance(origin, dict) else None
        self.destination = destination if isinstance(destination, dict) else None
        self.coords = coords

    @staticmethod
    def convert_coord_to_dict(coord):
        return {'lat': coord[1], 'long': coord[2]}


def process():
    shapes = [['shape_id', 'shape_pt_lat', 'shape_pt_lon', 'shape_pt_sequence']]
    # Open system.kml file in go/data/routes
    with open('{}/data/routes/system.kml'.format(PATH)) as file:
        doc = parser.parse(file)
        shape = None
        index = {}
        for t in doc.getiterator():

            # If the tag is a name, set name equal to the text contents of the name tag
            if re.sub('\{.*\}', '', t.tag).lower() == 'name':
                shape = Shape(t.text) if t.text not in Shape.objects else Shape.objects[t.text]

            # Save coordinates
            if re.sub('\{.*\}', '', t.tag).lower() == 'coordinates':
                # A new Path must be created for the discovered coordinates
                shape.add_path([re.split(',', x) for x in re.split('\s', t.text) if len(re.split(',', x)) == 3])

    # Open writer
    writer = open('{}/reports/gtfs/shapes.txt'.format(PATH), 'w')

    for obj in sorted(Shape.objects.keys()):
        shape = Shape.objects[obj]
        shape.order_paths()

        for path in shape.order:
            for coord in path.coords:
                writer.write('{}\n'.format(','.join([str(s) for s in [shape.name, coord[1], coord[0], shape.index]])))
                shape.index += 1

if __name__ == "__main__":
    process()

