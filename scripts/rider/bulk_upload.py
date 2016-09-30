import datetime
from dateutil import parser, tz
import xlsxwriter
import multiprocessing as mp

from src.scripts.constants import *
from src.scripts.rider.constants import BEGIN, BASELINE, INCREMENT, OUT_PATH
from src.scripts.utils.classes import DataModelTemplate
from src.scripts.utils.IOutils import *
from src.scripts.utils.send_requests import DataRequest


# READ FIRST!!!!!!!!
# This script may only be used once to pull rider data from the app, configure all IDs, and send it back to the
# database with the entire dataset in the correct order
# To be safe...turn on maintenance mode or alert all users to stop using the rider portion of the database until this is
# complete. First run a ridership report. Do a GIT commit on the data folder. Then run this script. Should something go
# wrong back up to that version/branch of the repository.

# Classes for converting IDs and I/O
class Metadata(DataModelTemplate):

    # REMOVE second entry in this tuple once full database upload complete----------------------------------------------
    json_path = ('{}/rider/metadata.json'.format(DATA_PATH), '{}/rider/get_metadata.json'.format(DATA_PATH))
    objects = {}
    meta_map = {}

    def set_object_attrs(self):
        new_id = abs(self.id) if self.id < 0 else self.id + 2383
        Metadata.meta_map[self.id] = new_id
        self.id = new_id


class Entry(DataModelTemplate):

    # REMOVE second entry in this tuple once full database upload complete----------------------------------------------
    json_path = ('{}/rider/entry.json'.format(DATA_PATH), '{}/rider/get_entry.json'.format(DATA_PATH))
    objects = {}

    def set_object_attrs(self):
        self.metadata = Metadata.meta_map[self.metadata]


# PULL FROM DATABASE
DataRequest('entry', '/rider/get_entry.json').get()
DataRequest('metadata', '/rider/get_metadata.json').get()

# LOAD AND CONVERT FILES
Metadata.load()
Entry.load()

# DELETE FROM DATABASE
DataRequest('entry', '/rider/get_entry.json').delete()
DataRequest('metadata', '/rider/get_metadata.json').delete()

# POST FINAL DATA TO DATABASE
Metadata.export()
Entry.export()
DataRequest('entry', '/rider/entry.json').post()
DataRequest('metadata', '/rider/metadata.json').post()
