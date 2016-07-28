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

from bike.views import *
from cyclist.views import *
from driver.views import *
from rider.views import *
from route.views import *
from stop.views import *
from vehicle.views import *


# Initialize router
router = routers.SimpleRouter()

# Bike
router.register(r'fleet', FleetViewSet)
router.register(r'steward', StewardViewSet)
router.register(r'bike', BikeViewSet)
router.register(r'bikegps', BikeGPSViewSet)
router.register(r'lock', LockViewSet)
router.register(r'asset', AssetViewSet)

# Cyclist
router.register(r'cyclist', CyclistViewSet)
router.register(r'checkinout', CheckInOutViewSet)

# Driver
router.register(r'driver', DriverViewSet)

# Rider
router.register(r'metadata', MetadataViewSet)
router.register(r'entry', EntryViewSet)

# Route
router.register(r'service', ServiceViewSet)
router.register(r'holiday', HolidayViewSet)
router.register(r'joint', JointViewSet)
router.register(r'schedule', ScheduleViewSet)
router.register(r'direction', DirectionViewSet)
router.register(r'segment', SegmentViewSet)
router.register(r'stopseq', StopSeqViewSet)
router.register(r'trip', TripViewSet)
router.register(r'stoptime', StopTimeViewSet)

# Stop
router.register(r'stop', StopViewSet)
router.register(r'geography', GeographyViewSet)
router.register(r'inventory', InventoryViewSet)

# Vehicle
router.register(r'vehicle', VehicleViewSet)
router.register(r'maintenance', MaintenanceViewSet)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/v1/', include(router.urls, namespace='apiv1')),
]

