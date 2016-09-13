import datetime
from dateutil import tz
from src.scripts.constants import REPORT_PATH


CHARS = list(map(chr, range(65, 91)))
BEGIN = datetime.datetime(2015, 8, 31, tzinfo=tz.gettz('America/Los_Angeles'))
PILOT = datetime.datetime(2016, 9, 30, tzinfo=tz.gettz('America/Los_Angeles'))
BASELINE = 19.4000
GOAL1 = 83.3333
INCREMENT = (GOAL1 - BASELINE) / abs(PILOT - BEGIN).days

OUT_PATH = '{}/rider'.format(REPORT_PATH)
