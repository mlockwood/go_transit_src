import datetime
from src.scripts.utils.functions import find_path

PATH = find_path('go')
BEGIN = datetime.datetime(2015, 8, 31)
PILOT = datetime.datetime(2016, 10, 31)
BASELINE = 19.4000
GOAL1 = 83.3333
INCREMENT = (GOAL1 - BASELINE) / abs(PILOT - BEGIN).days
