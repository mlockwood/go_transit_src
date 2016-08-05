import json
import os
import re
import requests

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "go_django.settings")

from django import setup
setup()
from django.contrib.auth.models import Group, User
from django.db.utils import IntegrityError

from src.scripts.constants import *
from src.scripts.utils.IOutils import load_json


ROOT = 'http://127.0.0.1:8000/api/v1'
HEADER = {'Authorization': 'token fc30ff32d078e97190558b7fdaf68fb392cec32d'}


class DatabaseLoader(object):

    models = {}  # {name: json_file}
    objects = {}

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
        cls.delete()
        cls.post()
        cls.objects = {}
        return True

    @classmethod
    def delete(cls):
        for name in cls.objects:
            res = requests.get('{}/{}/'.format(ROOT, name), headers=HEADER)
            while res.json()['results']:
                for item in res.json()['results']:
                    requests.delete('{}/{}/{}/'.format(ROOT, name, item['id']), headers=HEADER)
                res = requests.get('{}/{}/'.format(ROOT, name), headers=HEADER)
        return True

    @classmethod
    def post(cls):
        for name in cls.objects:
            for item in cls.objects[name].data:
                res = requests.post('{}/{}/'.format(ROOT, name), data=item, headers=HEADER)
                if (re.search('4\d\d', str(res.status_code)) and not re.search('already exists', str(res.json())) and
                        not re.search('unique set', str(res.json()))):
                    print(name, res.json())
        return True


class UserLoader(object):

    groups = {}
    json_file = '{}/user/user.json'.format(DATA_PATH)

    @classmethod
    def process(cls):
        # Load user.json
        with open(cls.json_file, 'r') as infile:
            data = json.load(infile)

            # For each user
            for end_user in data:

                # Set a user in the model
                try:
                    user = User.objects.create_user(**{
                        'username': end_user['username'],
                        'email': end_user['email'],
                        'password': end_user['password'],
                        'first_name': end_user['first_name'],
                        'last_name': end_user['last_name'],
                        'is_active': end_user['is_active'],
                        'is_staff': end_user['is_staff']
                    })
                except IntegrityError:
                    user = User.objects.get(username=end_user['username'])

                # Add groups to user
                for group in end_user['groups']:
                    if group not in cls.groups:
                        cls.groups[group] = Group.objects.get(name=group)
                    cls.groups[group].user_set.add(user)

                # Set end_user portion of the attributes
                requests.post('{}/end_user/'.format(ROOT), data={'id': end_user['id'], 'user': user.pk}, headers=HEADER)

        return True


class FirstLoader(DatabaseLoader):

    models = {
        'fleet': '{}/fleet/fleet.json'.format(DATA_PATH),
        'service': '{}/route/service.json'.format(DATA_PATH),
        'holiday': '{}/route/holiday.json'.format(DATA_PATH),
        'geography': '{}/stop/geography.json'.format(DATA_PATH),
        'vehicle': '{}/vehicle/vehicle.json'.format(DATA_PATH),
    }
    objects = {}


class SecondLoader(DatabaseLoader):

    models = {
        'bike': '{}/bike/bike.json'.format(DATA_PATH),
        'asset': '{}/fleet/asset.json'.format(DATA_PATH),
        'metadata': '{}/rider/metadata.json'.format(DATA_PATH),
        'joint': '{}/route/joint.json'.format(DATA_PATH),
        'stop': '{}/stop/stop.json'.format(DATA_PATH),
        # 'maintenance': '{}/maintenance.json'.format(DATA_PATH),
    }
    objects = {}


class ThirdLoader(DatabaseLoader):

    models = {
        # 'bike_gps': '{}/bike/bike_gps.json'.format(DATA_PATH),
        # 'lock': '{}/bike/lock.json'.format(DATA_PATH),
        # 'checkinout': '{}/checkinout.json'.format(DATA_PATH),
        'entry': '{}/rider/entry.json'.format(DATA_PATH),
        # 'schedule': '{}/route/schedule.json'.format(DATA_PATH),
        # 'direction': '{}/route/direction.json'.format(DATA_PATH),
        # 'stop_seq': '{}/route/stop_seq.json'.format(DATA_PATH),
    }
    objects = {}


class FourthLoader(DatabaseLoader):

    models = {
        'segment': '{}/route/segment.json'.format(DATA_PATH),
    }
    objects = {}


class FifthLoader(DatabaseLoader):

    models = {
        'trip': '{}/route/trip.json'.format(DATA_PATH),
    }
    objects = {}


class SixthLoader(DatabaseLoader):

    models = {
        'stop_time': '{}/route/stop_time.json'.format(DATA_PATH),
    }
    objects = {}


if __name__ == "__main__":
    # UserLoader.process()
    # FirstLoader.process()
    # SecondLoader.process()
    ThirdLoader.process()
    # FourthLoader.process()
    # FifthLoader.process()
    # SixthLoader.process()
