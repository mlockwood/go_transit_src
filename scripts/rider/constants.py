import datetime


CHARS = list(map(chr, range(65, 91)))

CONVERT_D = {'Sunday': 0, 'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4, 'Friday': 5, 'Saturday': 6}
CONVERT_A = {0: 'Sunday', 1: 'Monday', 2: 'Tuesday', 3: 'Wednesday', 4: 'Thursday', 5: 'Friday', 6: 'Saturday',
             7: 'Sunday'}
CONVERT_M = {1: 'JAN', 2: 'FEB', 3: 'MAR', 4: 'APR', 5: 'MAY', 6: 'JUN', 7: 'JUL', 8: 'AUG', 9: 'SEP', 10: 'OCT',
             11: 'NOV', 12: 'DEC'}

BEGIN = datetime.datetime(2015, 8, 31)
PILOT = datetime.datetime(2016, 10, 31)
BASELINE = 19.4000
GOAL1 = 83.3333
INCREMENT = (GOAL1 - BASELINE) / abs(PILOT - BEGIN).days
