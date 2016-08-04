from rest_framework import serializers

from . import models


class DayScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'operating',
            'start',
            'end'
        )
        model = models.DaySchedule


class CarpoolSerializer(serializers.ModelSerializer):
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
            'license',
            'occupancy',
            'hov_parking'
        )
        model = models.Carpool


class VanpoolSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'name',
            'agency',
            'monday',
            'tuesday',
            'wednesday',
            'thursday',
            'friday',
            'saturday',
            'sunday',
            'license',
            'occupancy',
            'hov_parking'
        )
        model = models.Vanpool
