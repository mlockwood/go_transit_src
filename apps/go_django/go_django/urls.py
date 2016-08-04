"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin

from rest_framework import routers

from agency.views import *
from bike.views import *
from fleet.views import *
from maintenance.views import *
from rider.views import *
from rideshare.views import *
from route.views import *
from stop.views import *
from user.views import *
from vehicle.views import *


# Initialize router
router = routers.SimpleRouter()

# Agency
router.register(r'agency', AgencyViewSet)

# Bike
router.register(r'bike', BikeViewSet)
router.register(r'bike_gps', BikeGPSViewSet)
router.register(r'check_in_out', CheckInOutViewSet)
router.register(r'lock', LockViewSet)

# Fleet
router.register(r'fleet', FleetViewSet)
router.register(r'asset', AssetViewSet)

# Maintenance
router.register(r'bike_damage', BikeDamageViewSet)
router.register(r'bike_inventory', BikeInventoryViewSet)
router.register(r'bike_maintenance', BikeMaintenanceViewSet)
router.register(r'bike_gps_damage', BikeGPSDamageViewSet)
router.register(r'bike_gps_inventory', BikeGPSInventoryViewSet)
router.register(r'bike_gps_maintenance', BikeGPSMaintenanceViewSet)
router.register(r'fleet_asset_damage', FleetAssetDamageViewSet)
router.register(r'fleet_asset_inventory', FleetAssetInventoryViewSet)
router.register(r'fleet_asset_maintenance', FleetAssetMaintenanceViewSet)
router.register(r'lock_damage', LockDamageViewSet)
router.register(r'lock_inventory', LockInventoryViewSet)
router.register(r'lock_maintenance', LockMaintenanceViewSet)
router.register(r'stop_damage', StopDamageViewSet)
router.register(r'stop_inventory', StopInventoryViewSet)
router.register(r'stop_maintenance', StopMaintenanceViewSet)
router.register(r'vehicle_damage', VehicleDamageViewSet)
router.register(r'vehicle_inventory', VehicleInventoryViewSet)
router.register(r'vehicle_maintenance', VehicleMaintenanceViewSet)

# Rider
router.register(r'metadata', MetadataViewSet)
router.register(r'entry', EntryViewSet)

# Route
router.register(r'direction', DirectionViewSet)
router.register(r'holiday', HolidayViewSet)
router.register(r'joint', JointViewSet)
router.register(r'schedule', ScheduleViewSet)
router.register(r'segment', SegmentViewSet)
router.register(r'service', ServiceViewSet)
router.register(r'stop_seq', StopSeqViewSet)
router.register(r'stop_time', StopTimeViewSet)
router.register(r'transfer', TransferViewSet)
router.register(r'trip', TripViewSet)

# Stop
router.register(r'stop', StopViewSet)
router.register(r'geography', GeographyViewSet)

# User
router.register(r'end_user', EndUserViewSet)

# Vehicle
router.register(r'vehicle', VehicleViewSet)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/v1/', include(router.urls, namespace='apiv1')),
]

