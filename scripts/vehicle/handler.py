import re
import uuid

from src.scripts.constants import *
from src.scripts.utils.classes import DataModelTemplate


class Vehicle(DataModelTemplate):

    json_path = '{}/vehicle.json'.format(DATA_PATH)
    objects = {}

    def set_objects(self):
        Vehicle.objects[self.license] = self

    @classmethod
    def txt_load(cls):
        reader = open('{}/ridership/vehicles.txt'.format(DATA_PATH), 'r')
        for row in reader:
            row = re.split(',', row.rstrip())
            Vehicle(**{
                'license': row[0]
            })


Vehicle.txt_load()
Vehicle.export()
