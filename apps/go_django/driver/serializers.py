from rest_framework import serializers

from . import models


class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'first',
            'last',
            'rank'
        )
        model = models.Driver
