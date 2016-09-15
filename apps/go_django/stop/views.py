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


class StopViewSet(viewsets.ModelViewSet):
    queryset = models.Stop.objects.all()
    serializer_class = serializers.StopSerializer


class GeographyViewSet(viewsets.ModelViewSet):
    queryset = models.Geography.objects.all()
    serializer_class = serializers.GeographySerializer


class ShelterViewSet(viewsets.ModelViewSet):
    queryset = models.Shelter.objects.all()
    serializer_class = serializers.ShelterSerializer


class SignViewSet(viewsets.ModelViewSet):
    queryset = models.Sign.objects.all()
    serializer_class = serializers.SignSerializer
