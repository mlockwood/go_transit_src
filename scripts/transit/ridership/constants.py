
CHARS = list(map(chr, range(65, 91)))
DATA_HEADER = ['boarding', 'time', 'count', 'destination']
META_HEADER = ['year', 'month', 'day', 'sheet', 'route', 'driver', 'license', 'start_shift', 'start_driving',
               'start_mileage', 'end_driving', 'end_shift', 'end_mileage']
INJECT_HEADER = ['stop', 'route', 'from', 'to', 'stop']

CONVERT_D = {'Sunday': 0, 'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4, 'Friday': 5, 'Saturday': 6}
CONVERT_A = {0: 'Sunday', 1: 'Monday', 2: 'Tuesday', 3: 'Wednesday', 4: 'Thursday', 5: 'Friday', 6: 'Saturday',
             7: 'Sunday'}
CONVERT_M = {1: 'JAN', 2: 'FEB', 3: 'MAR', 4: 'APR', 5: 'MAY', 6: 'JUN', 7: 'JUL', 8: 'AUG', 9: 'SEP', 10: 'OCT',
             11: 'NOV', 12: 'DEC'}
