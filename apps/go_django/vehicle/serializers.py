from rest_framework import serializers

from . import models


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'license',
            'make',
            'model'
        )
        model = models.Vehicle
