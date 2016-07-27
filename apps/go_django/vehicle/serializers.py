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


class MaintenanceSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'vehicle',
            'repair',
            'description',
            'cost',
            'repair_date'
        )
        model = models.Maintenance
