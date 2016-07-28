from rest_framework import serializers

from . import models


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


class DirectionSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'name',
            'description',
            'origin',
            'destination'
        )
        model = models.Direction


class SegmentSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'joint',
            'schedule',
            'dir_order',
            'route',
            'name',
            'direction'
        )
        model = models.Segment


class StopSeqSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'segment',
            'stop',
            'arrive',
            'depart',
            'timed',
            'display',
            'load_seq',
            'destination'
        )
        model = models.StopSeq


class TripSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'joint',
            'schedule',
            'segment',
            'direction',
            'start_loc',
            'end_loc',
            'base_time',
            'start_time',
            'end_time',
            'driver'
        )
        model = models.Trip


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
