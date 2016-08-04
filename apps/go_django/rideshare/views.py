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


class DayScheduleViewSet(viewsets.ModelViewSet):
    queryset = models.DaySchedule.objects.all()
    serializer_class = serializers.DayScheduleSerializer


class CarpoolViewSet(viewsets.ModelViewSet):
    queryset = models.Carpool.objects.all()
    serializer_class = serializers.CarpoolSerializer


class VanpoolViewSet(viewsets.ModelViewSet):
    queryset = models.Vanpool.objects.all()
    serializer_class = serializers.VanpoolSerializer
