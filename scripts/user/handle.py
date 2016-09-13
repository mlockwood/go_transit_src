import re
import uuid

from src.scripts.constants import *
from src.scripts.utils.classes import DataModelTemplate


class User(DataModelTemplate):

    json_path = '{}/user/user.json'.format(DATA_PATH)
    objects = {}


User.load()
User.export()
