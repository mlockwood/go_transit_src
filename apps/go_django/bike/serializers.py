from rest_framework import serializers

from . import models


class BikeSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'serial_number',
            'low_step',
            'fleet',
        )
        model = models.Bike


class BikeGPSSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'bike',
            'id',
            'serial_number',
            'wi_mm',
        )
        model = models.BikeGPS


class CheckInOutSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id'
            'fleet',
            'bike',
            'duration',
            'check_out',
            'check_in'
        )
        model = models.CheckInOut


class LockSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'bike',
            'id',
            'serial_number',
        )
        model = models.Lock

