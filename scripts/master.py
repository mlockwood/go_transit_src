import datetime


DATE = datetime.datetime.today() # (year, month, day) -> this should be the first day of the GTFS you wish to publish
RIDERSHIP = False  # toggle to run ridership and produce reports...download is VERY slow
ROUTES = True  # toggle to run updated route planning (GTFS, website, and timepoints)


# Ridership
if RIDERSHIP:
    from src.scripts.rider.ridership import process
    process()

# Route planning; remember to put the current shapes.kml file in data/route/kml before running to ensure shapes are
# properly represented. After running validate shapes conversion by viewing the report/gtfs/test folder
if ROUTES:
    from src.scripts.route.route import create, load
    create(DATE)
    load(DATE)

    from src.scripts.gtfs.gtfs import create_gtfs
    from src.scripts.route.timepoint import publish_timepoints
    from src.scripts.web.web_pages import publish

    create_gtfs(DATE)
    publish(DATE)
    publish_timepoints(DATE)