from rest_framework import serializers

from . import models


class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        extra_kwargs = {
            'first': {'write_only': True},
            'last': {'write_only': True}
        }
        fields = (
            'id'
            'first',
            'last',
            'hired'
        )
        model = models.Driver


class StopSerializer(serializers.ModelSerializer):
    class Meta:
        extra_kwargs = {
            'first': {'write_only': True},
            'last': {'write_only': True}
        }
        fields = (
            'id'
            'first',
            'last',
            'hired'
        )
        model = models.Driver
