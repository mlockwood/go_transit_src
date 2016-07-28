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
            'operating',
            'phone',
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
        )
        model = models.Steward


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


class LockSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'bike',
            'id',
            'serial_number',
        )
        model = models.Lock


class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'fleet',
            'id',
            'asset_type',
        )
        model = models.Asset
