from rest_framework import serializers

from . import models


class ServiceSerializer(serializers.ModelSerializer):
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
            'start_date',
            'end_date',
            'text'
        )
        model = models.Service