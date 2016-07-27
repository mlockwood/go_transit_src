from rest_framework import generics, mixins, permissions, viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from . import models
from . import serializers


class IsSuperUser(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_superuser and request.method == 'DELETE':
            return False
        return True


class FleetViewSet(viewsets.ModelViewSet):
    queryset = models.Fleet.objects.all()
    serializer_class = serializers.FleetSerializer


class StewardViewSet(viewsets.ModelViewSet):
    queryset = models.Steward.objects.all()
    serializer_class = serializers.StewardSerializer


class BikeViewSet(viewsets.ModelViewSet):
    queryset = models.Bike.objects.all()
    serializer_class = serializers.BikeSerializer


class BikeGPSViewSet(viewsets.ModelViewSet):
    queryset = models.BikeGPS.objects.all()
    serializer_class = serializers.BikeGPSSerializer


class LockViewSet(viewsets.ModelViewSet):
    queryset = models.Lock.objects.all()
    serializer_class = serializers.LockSerializer


class AssetViewSet(viewsets.ModelViewSet):
    queryset = models.Asset.objects.all()
    serializer_class = serializers.AssetSerializer
