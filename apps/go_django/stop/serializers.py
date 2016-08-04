from rest_framework import serializers

from . import models


class StopSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'name',
            'location',
            'description',
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
            'name',
            'minimum',
            'maximum'
        )
        model = models.Geography

