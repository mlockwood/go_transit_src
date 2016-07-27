import json
import requests

from src.scripts.constants import PATH


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
        cls.delete()
        cls.post()
        return True

    @classmethod
    def delete(cls):
        for name in cls.objects:
            res = requests.get('{}/{}/'.format(cls.root, name), headers=cls.header)
            for item in res.json()['results']:
                requests.delete('{}/{}/{}/'.format(cls.root, name, item['id']), headers=cls.header)
        return True

    @classmethod
    def post(cls):
        for name in cls.objects:
            for item in cls.objects[name].data:
                requests.post('{}/{}/'.format(cls.root, name), data=item, headers=cls.header)
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


class FirstLoad(DatabaseLoader):

    models = {}