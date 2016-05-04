import datetime

DATE = datetime.datetime(2016, 4, 25)
LAX = 300
STOP_TIME_HEADER = ['trip_id', 'stop_id', 'gps_ref', 'direction', 'arrival', 'departure', 'stop_seq', 'timepoint',
                    'pickup', 'dropoff', 'display', 'driver', 'joint']
DISPLAY_ALL = True

SCHEDULE_HEADER = '<!DOCTYPE html>\n<html lang="en">\n\t<head>\n\t<meta charset="UTF-8">\n\
\t<title>GO Transit Schedule</title>\n\t<!-- Latest compiled and minified CSS -->\n\
\t<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css"\n\
\t\tintegrity="sha384-1q8mTJOASx8j1Au+a5WDVnPi2lkFfwwEAa8hDDdjZlpLegxhjVME1fgjWPGmkzs7" crossorigin="anonymous">\
\t<link rel="stylesheet" href="css/go.css">\n\t<link rel="stylesheet" href="css/schedule.css">\n</head>\n<body>\n'

TIMETABLE_HEADER = '<!DOCTYPE html>\n<html lang="en">\n\t<head>\n\t<meta charset="UTF-8">\n\
\t<title>GO Transit Timetable</title>\n\t<!-- Latest compiled and minified CSS -->\n\
\t<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css"\n\
\t\tintegrity="sha384-1q8mTJOASx8j1Au+a5WDVnPi2lkFfwwEAa8hDDdjZlpLegxhjVME1fgjWPGmkzs7" crossorigin="anonymous">\
\t<link rel="stylesheet" href="css/go.css">\n\t<link rel="stylesheet" href="css/timetable.css">\n</head>\n<body>\n\
\n\t<div class="col-md-6">'

TIMETABLE_FOOTER = '\n\t\t</br>\n\n\t\t<div class="col-md-10" id="footerText">\n\t\t\t<p>For questions or assistance \
planning your trip, please call the Transit Supervisor at (253) 966-3939.</p>\n\t\t\t<p>All times are estimated for \
public guidance only. GO Transit does not operate on Federal Holidays.</p>\n\t\t\t<p>For current route maps and \
schedules please visit www.facebook.com/GoLewisMcChord.</p>\n\t\t</div>\n\n\t\t<div class="col-md-2">\n\t\t\t<img \
src="img/go_logo.jpg" id="footerImg" />\n\t\t</div>\n\n\t</div>\n\n</body>\n</html>'

ORDER = {'Sunday - Thursday': 1, 'Monday - Friday': 2, 'Friday & Saturday': 3, 'Saturday & Sunday': 4}
