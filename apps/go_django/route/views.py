from django.shortcuts import render

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


class HolidayViewSet(viewsets.ModelViewSet):
    queryset = models.Holiday.objects.all()
    serializer_class = serializers.HolidaySerializer


class JointViewSet(viewsets.ModelViewSet):
    queryset = models.Joint.objects.all()
    serializer_class = serializers.JointSerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = models.Route.objects.all()
    serializer_class = serializers.RouteSerializer


class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = models.Schedule.objects.all()
    serializer_class = serializers.ScheduleSerializer


class SegmentViewSet(viewsets.ModelViewSet):
    queryset = models.Segment.objects.all()
    serializer_class = serializers.SegmentSerializer


class SegmentOrderViewSet(viewsets.ModelViewSet):
    queryset = models.SegmentOrder.objects.all()
    serializer_class = serializers.SegmentOrderSerializer


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = models.Service.objects.all()
    serializer_class = serializers.ServiceSerializer


class StopSeqViewSet(viewsets.ModelViewSet):
    queryset = models.StopSeq.objects.all()
    serializer_class = serializers.StopSeqSerializer


class StopTimeViewSet(viewsets.ModelViewSet):
    queryset = models.StopTime.objects.all()
    serializer_class = serializers.StopTimeSerializer


class TripViewSet(viewsets.ModelViewSet):
    queryset = models.Trip.objects.all()
    serializer_class = serializers.TripSerializer
