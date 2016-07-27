from src.scripts.utils.classes import DataModelTemplate
from src.scripts.constants import PATH


class Stop(DataModelTemplate):

    json_path = '{}/data/stop.json'.format(PATH)
    locations = {}

    def set_object_attrs(self):
        if self.location not in Stop.locations:
            Stop.locations[self.location] = {}
        Stop.locations[self.location][self.id[3]] = self


class Geography(DataModelTemplate):

    json_path = '{}/data/geography.json'.format(PATH)
    objects = {}


class Inventory(DataModelTemplate):

    json_path = '{}/data/inventory.json'.format(PATH)
    objects = {}

    def set_objects(self):
        Inventory.objects[self.timestamp, self.stop] = self


Stop.load()

if __name__ == '__main__':
    Geography.load()
    Inventory.load()
