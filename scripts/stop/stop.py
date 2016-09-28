from src.scripts.utils.classes import DataModelTemplate
from src.scripts.constants import *


class Stop(DataModelTemplate):

    json_path = '{}/stop/stop.json'.format(DATA_PATH)
    objects = {}
    locations = {}

    def __repr__(self):
        return '<Stop {}>'.format(self.id)

    def set_object_attrs(self):
        if self.location not in Stop.locations:
            Stop.locations[self.location] = {}
        Stop.locations[self.location][self.id[3]] = self


class Geography(DataModelTemplate):

    json_path = '{}/stop/geography.json'.format(DATA_PATH)
    objects = {}

    def __repr__(self):
        return '<Geography {}>'.format(self.id)


class Shelter(DataModelTemplate):

    objects = {}
    json_path = '{}/stop/shelter.json'.format(DATA_PATH)

    def __repr__(self):
        return '<Shelter for stop {}>'.format(self.stop)


class Sign(DataModelTemplate):

    objects = {}
    json_path = '{}/stop/sign.json'.format(DATA_PATH)
    gen_id = 1

    def __repr__(self):
        return '<Sign for stop {}>'.format(self.stop)
