from django.contrib import admin

from . import models


class MaintenanceInline(admin.StackedInline):
    model = models.Maintenance


class VehicleAdmin(admin.ModelAdmin):
    inlines = [MaintenanceInline]


admin.site.register(models.Vehicle, VehicleAdmin)
