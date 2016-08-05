import re
import uuid

from src.scripts.constants import *
from src.scripts.utils.classes import DataModelTemplate


class User(DataModelTemplate):

    json_path = '{}/user/user.json'.format(DATA_PATH)
    objects = {}

    def set_objects(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        User.objects[self.id] = self


User.load()
