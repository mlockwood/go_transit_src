from rest_framework import serializers

from . import models


class StopSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'name',
            'location',
            'location_type',
            'description',
            'geography',
            'lat',
            'lng',
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


class ShelterSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'stop',
            'design',
            'size',
            'color',
            'solar_lighting',
            'ad_panel'
        )
        model = models.Shelter


class SignSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'stop',
            'anchor',
            'design',
            'midi_guide'
        )
        model = models.Sign
