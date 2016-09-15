from rest_framework import serializers

from . import models


class BikeDamageSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'asset',
            'damage',
            'description',
            'date'
        )
        model = models.BikeDamage


class BikeInventorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'asset',
            'timestamp',
            'code',
            'notes'
        )
        model = models.BikeInventory


class BikeMaintenanceSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'damage_report',
            'repair',
            'description',
            'cost',
            'repair_date'
        )
        model = models.BikeMaintenance


class BikeGPSDamageSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'asset',
            'damage',
            'description',
            'date'
        )
        model = models.BikeGPSDamage


class BikeGPSInventorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'asset',
            'timestamp',
            'code',
            'notes'
        )
        model = models.BikeGPSInventory


class BikeGPSMaintenanceSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'damage_report',
            'repair',
            'description',
            'cost',
            'repair_date'
        )
        model = models.BikeGPSMaintenance


class FleetAssetDamageSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'asset',
            'damage',
            'description',
            'date'
        )
        model = models.FleetAssetDamage


class FleetAssetInventorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'asset',
            'timestamp',
            'code',
            'notes'
        )
        model = models.FleetAssetInventory


class FleetAssetMaintenanceSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'damage_report',
            'repair',
            'description',
            'cost',
            'repair_date'
        )
        model = models.FleetAssetMaintenance


class LockDamageSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'asset',
            'damage',
            'description',
            'date'
        )
        model = models.LockDamage


class LockInventorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'asset',
            'timestamp',
            'code',
            'notes'
        )
        model = models.LockInventory


class LockMaintenanceSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'damage_report',
            'repair',
            'description',
            'cost',
            'repair_date'
        )
        model = models.LockMaintenance


class ShelterDamageSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'asset',
            'damage',
            'description',
            'date'
        )
        model = models.ShelterDamage


class ShelterInventorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'asset',
            'timestamp',
            'code',
            'notes'
        )
        model = models.ShelterInventory


class ShelterMaintenanceSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'damage_report',
            'repair',
            'description',
            'cost',
            'repair_date'
        )
        model = models.ShelterMaintenance
        

class SignDamageSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'asset',
            'damage',
            'description',
            'date'
        )
        model = models.SignDamage


class SignInventorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'asset',
            'timestamp',
            'code',
            'notes'
        )
        model = models.SignInventory


class SignMaintenanceSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'damage_report',
            'repair',
            'description',
            'cost',
            'repair_date'
        )
        model = models.SignMaintenance


class VehicleDamageSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'asset',
            'damage',
            'description',
            'date'
        )
        model = models.VehicleDamage


class VehicleInventorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'asset',
            'timestamp',
            'code',
            'notes'
        )
        model = models.VehicleInventory


class VehicleMaintenanceSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'asset',
            'damage_report',
            'repair',
            'description',
            'cost',
            'repair_date'
        )
        model = models.VehicleMaintenance
