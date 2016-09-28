from rest_framework import serializers

from . import models


class HolidaySerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'holiday'
        )
        model = models.Holiday


class JointSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'routes',
            'description',
            'service',
            'headway'
        )
        model = models.Joint


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'short_name',
            'long_name',
            'description',
            'color',
            'text_color'
        )
        model = models.Route


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'joint',
            'start',
            'end',
            'offset'
        )
        model = models.Schedule


class SegmentSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'route',
            'direction',
            'description'
        )
        model = models.Segment


class SegmentOrderSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'schedule',
            'order',
            'segment',
            'dir_type'
        )
        model = models.SegmentOrder


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'monday',
            'tuesday',
            'wednesday',
            'thursday',
            'friday',
            'saturday',
            'sunday',
            'start_date',
            'end_date',
            'text'
        )
        model = models.Service


class StopSeqSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'segment',
            'stop',
            'arrive',
            'depart',
            'timed',
        )
        model = models.StopSeq


class StopTimeSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'trip',
            'stop',
            'arrive',
            'depart',
            'gtfs_depart',
            'arrive_24p',
            'depart_24p',
            'gtfs_depart_24p',
            'order',
            'timepoint',
            'pickup',
            'dropoff',
            'display'
        )
        model = models.StopTime


class TripSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'schedule',
            'direction',
            'start_loc',
            'end_loc',
            'start_time',
            'driver'
        )
        model = models.Trip