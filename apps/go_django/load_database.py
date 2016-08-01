import inspect
import json
import re
import requests
import sys

from src.scripts.constants import *


class DatabaseLoader(object):

    header = {'Authorization': 'token 9036073dba260f556352e828b71ff7dde44ebe44'}
    models = {}  # {name: json_file}
    objects = {}
    root = 'http://127.0.0.1:8000/api/v1'

    def __init__(self, name, json_file):
        self.name = name
        self.json_file = json_file
        self.data = self.load_data()
        self.__class__.objects[name] = self

    def load_data(self):
        with open(self.json_file, 'r') as infile:
            return json.load(infile)

    @classmethod
    def process(cls):
        for obj in cls.models:
            cls(obj, cls.models[obj])
        # cls.delete()
        cls.post()
        cls.objects = {}
        return True

    @classmethod
    def delete(cls):
        for name in cls.objects:
            res = requests.get('{}/{}/'.format(cls.root, name), headers=cls.header)
            while res.json()['results']:
                for item in res.json()['results']:
                    requests.delete('{}/{}/{}/'.format(cls.root, name, item['id']), headers=cls.header)
                res = requests.get('{}/{}/'.format(cls.root, name), headers=cls.header)
        return True

    @classmethod
    def post(cls):
        for name in cls.objects:
            for item in cls.objects[name].data:
                res = requests.post('{}/{}/'.format(cls.root, name), data=item, headers=cls.header)
                if (re.search('4\d\d', str(res.status_code)) and not re.search('already exists', str(res.json())) and
                        not re.search('unique set', str(res.json()))):
                    print(name, res.json())
        return True


data = [
    {
        "id": 1,
        "name": "Madigan",
        "minimum": 100,
        "maximum": 139
    },
    {
        "id": 2,
        "name": "Hillside",
        "minimum": 140,
        "maximum": 159
    },
    {
        "id": 3,
        "name": "Jackson A",
        "minimum": 160,
        "maximum": 169
    },
    {
        "id": 4,
        "name": "Jackson B",
        "minimum": 170,
        "maximum": 179
    }
]


class FirstLoader(DatabaseLoader):

    models = {
        'fleet': '{}/fleet.json'.format(DATA_PATH),
        # 'cyclist': '{}/cyclist.json'.format(DATA_PATH),
        'driver': '{}/driver.json'.format(DATA_PATH),
        'service': '{}/service.json'.format(DATA_PATH),
        'holiday': '{}/holiday.json'.format(DATA_PATH),
        'geography': '{}/geography.json'.format(DATA_PATH),
        'vehicle': '{}/vehicle.json'.format(DATA_PATH),
    }
    objects = {}


class SecondLoader(DatabaseLoader):

    models = {
        # 'steward': '{}/steward.json'.format(DATA_PATH),
        'bike': '{}/bike.json'.format(DATA_PATH),
        'asset': '{}/asset.json'.format(DATA_PATH),
        'metadata': '{}/metadata.json'.format(DATA_PATH),
        'joint': '{}/joint.json'.format(DATA_PATH),
        'stop': '{}/stop.json'.format(DATA_PATH),
        # 'maintenance': '{}/maintenance.json'.format(DATA_PATH),
    }
    objects = {}


class ThirdLoader(DatabaseLoader):

    models = {
        'bikegps': '{}/bike_gps.json'.format(DATA_PATH),
        'lock': '{}/lock.json'.format(DATA_PATH),
        # 'checkinout': '{}/checkinout.json'.format(DATA_PATH),
        'entry': '{}/entry.json'.format(DATA_PATH),
        'schedule': '{}/schedule.json'.format(DATA_PATH),
        'direction': '{}/direction.json'.format(DATA_PATH),
        'stopseq': '{}/stop_seq.json'.format(DATA_PATH),
        'inventory': '{}/inventory.json'.format(DATA_PATH),
    }
    objects = {}


class FourthLoader(DatabaseLoader):

    models = {
        'segment': '{}/segment.json'.format(DATA_PATH),
    }
    objects = {}


class FifthLoader(DatabaseLoader):

    models = {
        'trip': '{}/trip.json'.format(DATA_PATH),
    }
    objects = {}


class SixthLoader(DatabaseLoader):

    models = {
        'stoptime': '{}/stop_time.json'.format(DATA_PATH),
    }
    objects = {}


if __name__ == "__main__":
    FirstLoader.process()
    SecondLoader.process()
    ThirdLoader.process()
    FourthLoader.process()
    FifthLoader.process()
    SixthLoader.process()
