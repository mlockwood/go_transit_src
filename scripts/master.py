import datetime

from src.scripts.gtfs.gtfs import create_gtfs
from src.scripts.rider.ridership import process
from src.scripts.route.timepoint import publish_timepoints
from src.scripts.web.web_pages import publish


DATE = datetime.datetime.today() # (year, month, day) -> this should be the first day of the GTFS you wish to publish


# Ridership
process()

# Route planning; remember to put the current shapes.kml file in data/route/kml before running to ensure shapes are
# properly represented. After running validate shapes conversion by viewing the report/gtfs/test folder
create_gtfs(DATE)
publish(DATE)
publish_timepoints(DATE)