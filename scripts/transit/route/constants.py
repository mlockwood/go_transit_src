import datetime

DATE = datetime.datetime(2016, 4, 25)
LAX = 300
STOP_TIME_HEADER = ['trip_id', 'stop_id', 'gps_ref', 'direction', 'arrival', 'departure', 'stop_seq', 'timepoint',
                    'pickup', 'dropoff', 'display', 'driver', 'joint']
DISPLAY_ALL = True

SCHEDULE_TEXT = '<!DOCTYPE html>\n' + '<html lang="en">\n' + '\t<head>\n' + '\t<meta charset="UTF-8">\n\
    \t<title>Schedule</title>\n' + '\t<!-- Latest compiled and minified CSS -->\n\
    \t<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css"\n\
    \t\tintegrity="sha384-1q8mTJOASx8j1Au+a5WDVnPi2lkFfwwEAa8hDDdjZlpLegxhjVME1fgjWPGmkzs7" crossorigin="anonymous">\
    \t<link rel="stylesheet" href="css/go.css">\n' + '\t<link rel="stylesheet" href="css/schedule.css">\n' + '</head>\n\
    <body>\n'
