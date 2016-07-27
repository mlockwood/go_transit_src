from rest_framework import serializers

from . import models


class StopSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'name',
            'location',
            'description',
            'gps_ref',
            'geography',
            'lat',
            'lng',
            'signage',
            'shelter',
            'operating',
            'speed',
            'available'
        )
        model = models.Stop


class GeographySerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'geography',
            'minimum',
            'maximum'
        )
        model = models.Geography


class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'stop',
            'timestamp',
            'code',
            'notes'
        )
        model = models.Inventory
