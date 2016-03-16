

import datetime
from src.scripts.path_setter import find_path

path = find_path('go')
begin = datetime.date(2015, 8, 31)
pilot = datetime.date(2016, 10, 31)
baseline = 19.4000
goal_1 = 83.3333
increment = (goal_1 - baseline) / abs(pilot - begin).days
