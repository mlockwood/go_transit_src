import datetime

# DATE should be the first day of the GTFS you wish to publish and is today by default
DATE = datetime.datetime.today()
# DATE = datetime.datetime(2016, 10, 10) # (year, month, day)
RIDERSHIP = False  # toggle to run ridership and produce reports...download is VERY slow
ROUTES = True  # toggle to run updated route planning (GTFS, website, and timepoints)


# Ridership; once ALL data is in final database remember to modify rider/ridership.py and use rider/bulk_upload.py
if RIDERSHIP:
    from src.scripts.rider.ridership import process
    process()

# Route planning; remember to put the current shapes.kml file in data/route/kml before running to ensure shapes are
# properly represented.
if ROUTES:
    from src.scripts.route.route import create
    create(DATE)
    print('Finished creating routes.')

    from src.scripts.gtfs.gtfs import create_gtfs
    from src.scripts.route.timepoint import publish_timepoints
    from src.scripts.web.web_pages import publish

    create_gtfs(DATE)  # src/scripts/gtfs/gtfs.py
    print('GTFS created. Verify shape orderings in Google my maps using outputs in /reports/gtfs/test/')
    publish(DATE)  # src/scripts/web/web_pages.py
    print('Web pages created.')
    publish_timepoints(DATE)    # src/scripts/route/timepoint.py
    print('Timepoints created.')
