from rest_framework import serializers

from . import models


class MetadataSerializer(serializers.ModelSerializer):
    entries = serializers.StringRelatedField(many=True)

    class Meta:
        fields = (
            'id',
            'schedule',
            'vehicle',
            'login',
            'start_mileage',
            'end_mileage',
            'logout',
            'entries'
        )
        model = models.Metadata


class EntrySerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'metadata',
            'on',
            'time',
            'count',
            'off'
        )
        model = models.Entry
