from django.contrib import admin

from . import models


admin.site.register(models.BikeDamage)
admin.site.register(models.BikeInventory)
admin.site.register(models.BikeMaintenance)
admin.site.register(models.BikeGPSDamage)
admin.site.register(models.BikeGPSInventory)
admin.site.register(models.BikeGPSMaintenance)
admin.site.register(models.FleetAssetDamage)
admin.site.register(models.FleetAssetInventory)
admin.site.register(models.FleetAssetMaintenance)
admin.site.register(models.LockDamage)
admin.site.register(models.LockInventory)
admin.site.register(models.LockMaintenance)
admin.site.register(models.ShelterDamage)
admin.site.register(models.ShelterInventory)
admin.site.register(models.ShelterMaintenance)
admin.site.register(models.SignDamage)
admin.site.register(models.SignInventory)
admin.site.register(models.SignMaintenance)
admin.site.register(models.VehicleDamage)
admin.site.register(models.VehicleInventory)
admin.site.register(models.VehicleMaintenance)