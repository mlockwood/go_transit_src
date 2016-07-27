from rest_framework import serializers

from . import models


class FleetSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'name',
            'description',
            'lat',
            'lng',
            'operation',
            'phone_number',
            'schedule'
        )
        model = models.Fleet


class StewardSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'first_name',
            'last_name',
            'phone',
            'email',
            'fleet',
            'status',
            'history'
        )
        model = models.Steward


class BikeSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'serial_number',
            'low_step',
            'fleet',
            'history'
        )
        model = models.Bike


class BikeGPSSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'bike',
            'id',
            'serial_number',
            'wi_mm',
            'history'
        )
        model = models.BikeGPS


class LockSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'bike',
            'id',
            'serial_number',
            'history'
        )
        model = models.Lock


class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'fleet',
            'id',
            'asset_type',
            'history'
        )
        model = models.Asset
