import re
import uuid

from src.scripts.constants import *
from src.scripts.utils.classes import DataModelTemplate


class Driver(DataModelTemplate):

    json_path = '{}/driver.json'.format(DATA_PATH)

    @classmethod
    def txt_load(cls):
        reader = open('{}/ridership/drivers.txt'.format(DATA_PATH), 'r')
        for row in reader:
            row = re.split(',', row.rstrip())
            Driver(**{
                'id': str(uuid.uuid4()),
                'first': row[0],
                'last': row[1],
                'rank': row[2]
            })