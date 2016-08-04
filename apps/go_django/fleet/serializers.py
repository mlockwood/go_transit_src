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


class FleetAssetSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'fleet',
            'id',
            'asset_type',
        )
        model = models.FleetAsset
