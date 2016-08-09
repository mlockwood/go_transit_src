import json
import re
import requests

from src.scripts.constants import *


LOCAL_ROOT = 'http://127.0.0.1:8000/api/v1'
LOCAL_HEADER = {'Authorization': 'token fc30ff32d078e97190558b7fdaf68fb392cec32d'}

ROOT = 'https://golewismcchord.herokuapp.com/api/v1'
HEADER = {'Authorization': 'token 073a1a8db17a0b6241d95bc457f62989d71c7f88'}


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
        # cls.delete()
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
                    print(name, res.json(), item)
        return True


class UserLoader(object):

    groups = {}
    group_file = '{}/user/group.json'.format(DATA_PATH)
    user_file = '{}/user/user.json'.format(DATA_PATH)

    @classmethod
    def process(cls):
        # Load group.json
        with open(cls.group_file, 'r') as infile:
            data = json.load(infile)

            # For each group
            for group in data:
                requests.post('{}/group/'.format(ROOT), data=group, headers=HEADER)

        # Load user.json
        with open(cls.user_file, 'r') as infile:
            data = json.load(infile)

            # For each user
            for end_user in data:

                # Set the user
                user = {
                    'username': end_user['username'],
                    'email': end_user['email'],
                    'password': end_user['password'],
                    'groups': [int(i) + 6 for i in end_user['groups']],
                    'first_name': end_user['first_name'],
                    'last_name': end_user['last_name'],
                    'is_active': end_user['is_active'],
                    'is_staff': end_user['is_staff']
                }
                res = requests.post('{}/user/'.format(ROOT), data=user, headers=HEADER)
                if (re.search('4\d\d', str(res.status_code)) and not re.search('already exists', str(res.json())) and
                        not re.search('unique set', str(res.json()))):
                    print('user', res.json(), user)

                # Set end_user portion of the attributes
                res = requests.post('{}/end_user/'.format(ROOT), data={'id': end_user['id'],
                                    'user': end_user['username']}, headers=HEADER)
                if (re.search('4\d\d', str(res.status_code)) and not re.search('already exists', str(res.json())) and
                        not re.search('unique set', str(res.json()))):
                    print('end_user', res.json(), user)

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
        'maintenance': '{}/maintenance.json'.format(DATA_PATH),
    }
    objects = {}


class ThirdLoader(DatabaseLoader):

    models = {
        'bike_gps': '{}/bike/bike_gps.json'.format(DATA_PATH),
        'lock': '{}/bike/lock.json'.format(DATA_PATH),
        'checkinout': '{}/checkinout.json'.format(DATA_PATH),
        'entry': '{}/rider/entry.json'.format(DATA_PATH),
        'schedule': '{}/route/schedule.json'.format(DATA_PATH),
        'direction': '{}/route/direction.json'.format(DATA_PATH),
        'stop_seq': '{}/route/stop_seq.json'.format(DATA_PATH),
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
    UserLoader.process()
    FirstLoader.process()
    # SecondLoader.process()
    # ThirdLoader.process()
    # FourthLoader.process()
    # FifthLoader.process()
    # SixthLoader.process()
