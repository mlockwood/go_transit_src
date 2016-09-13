import json
import re
import requests

from src.scripts.constants import *


LOCAL_ROOT = 'http://127.0.0.1:8000/api/v1'
LOCAL_HEADER = {'Authorization': 'token fc30ff32d078e97190558b7fdaf68fb392cec32d'}

ROOT = 'https://golewismcchord.herokuapp.com/api/v1'
HEADER = {'Authorization': 'token a3ef1e8d6724c13e58f86bc21261e8c7847d56dc'}

WIMM_ROOT = 'https://system.boomerangbike.com/api/v1/lewis_mcchord'
WIMM_HEADER = {'Authorization': 'token 015a10a2bb5a4c483b97137d30ddfb4e',
               'password': 'jblm'}


res = requests.get('{}/trips'.format(WIMM_ROOT), headers=WIMM_HEADER)
# print(res)


def print_res(res, name, obj=None):
    if (re.search('4\d\d', str(res.status_code)) and not re.search('already exists', str(res.json())) and
            not re.search('unique set', str(res.json()))):
        print(name, res.json(), obj)


def get_data(name, json_file):
    data = []
    # Get the entry list to all results
    res = requests.get('{}/{}/'.format(ROOT, name), headers=HEADER)
    # Copy results from each page to data
    while res:
        data += res.json()['results']
        res = requests.get(res.json()['next'], headers=HEADER) if res.json()['next'] else None

    # Export data to json_file
    with open(json_file, 'w') as outfile:
        json.dump(data, outfile, indent=4, sort_keys=True)
    return True


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
                try:
                    res = requests.post('{}/{}/'.format(ROOT, name), data=item, headers=HEADER)
                except:
                    answer = None
                    while not answer:
                        answer = input('Server connection has been interrupted. Reset dynos. (Press anything)')
                    res = requests.post('{}/{}/'.format(ROOT, name), data=item, headers=HEADER)
                print_res(res, name, item)
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
            for user in data:

                # Set the user
                user_json = {
                    'username': user['id'],
                    'password': user['last_name'].lower(),
                    'email': user['id'],
                    'groups': [int(i) for i in user['groups']],
                    'first_name': user['first_name'],
                    'last_name': user['last_name'],
                    'is_active': user['is_active'],
                    'is_staff': user['is_staff']
                }
                res = requests.post('{}/user/'.format(ROOT), data=user_json, headers=HEADER)
                print_res(res, 'user', user_json)

            # After all users have been loaded set their password and end_user id
            res = requests.get('{}/user/'.format(ROOT), headers=HEADER)
            while res:
                for item in res.json()['results']:
                    user = requests.get('{}/user/{}'.format(ROOT, item['id']), headers=HEADER).json()

                    # Set user portion of the attributes
                    end_res = requests.post('{}/end_user/'.format(ROOT), data={'id': user['username'],
                                                                               'user': user['id']}, headers=HEADER)
                    print_res(end_res, 'end_user', user['username'])

                res = requests.get(res.json()['next'], headers=HEADER) if res.json()['next'] else None

        return True


class FirstLoader(DatabaseLoader):

    models = {
        'agency': '{}/agency/agency.json'.format(DATA_PATH),
        'fleet': '{}/fleet/fleet.json'.format(DATA_PATH),
        # 'service': '{}/route/service.json'.format(DATA_PATH),
        # 'holiday': '{}/route/holiday.json'.format(DATA_PATH),
        'geography': '{}/stop/geography.json'.format(DATA_PATH),
        'vehicle': '{}/vehicle/vehicle.json'.format(DATA_PATH),
    }
    objects = {}


class SecondLoader(DatabaseLoader):

    models = {
        'bike': '{}/bike/bike.json'.format(DATA_PATH),
        'asset': '{}/fleet/asset.json'.format(DATA_PATH),
        # 'metadata': '{}/rider/metadata.json'.format(DATA_PATH),
        # 'joint': '{}/route/joint.json'.format(DATA_PATH),
        'stop': '{}/stop/stop.json'.format(DATA_PATH),
    }
    objects = {}


class ThirdLoader(DatabaseLoader):

    models = {
        'bike_gps': '{}/bike/bike_gps.json'.format(DATA_PATH),
        'lock': '{}/bike/lock.json'.format(DATA_PATH),
        # 'checkinout': '{}/checkinout.json'.format(DATA_PATH),
        # 'entry': '{}/rider/entry.json'.format(DATA_PATH),
        # 'schedule': '{}/route/schedule.json'.format(DATA_PATH),
        # 'direction': '{}/route/direction.json'.format(DATA_PATH),
        # 'stop_seq': '{}/route/stop_seq.json'.format(DATA_PATH),
        # 'transfer': '{}/route/transfer.json'.format(DATA_PATH),
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
    # ThirdLoader.process()
    # FourthLoader.process()
    # FifthLoader.process()
    # SixthLoader.process()
    get_data('metadata', '{}/rider/get_metadata.json'.format(DATA_PATH))
    get_data('entry', '{}/rider/get_entry.json'.format(DATA_PATH))
    print('Done')
