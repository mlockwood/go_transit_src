from django.contrib import admin

from . import models


class BikeGPSInline(admin.StackedInline):
    model = models.BikeGPS


class LockInline(admin.StackedInline):
    model = models.Lock


class AssetInline(admin.StackedInline):
    model = models.Asset


class FleetAdmin(admin.ModelAdmin):
    inlines = [AssetInline]
    search_fields = ['id', 'name', 'description', 'schedule']


class BikeAdmin(admin.ModelAdmin):
    inlines = [BikeGPSInline, LockInline]
    list_filter = ['fleet', 'low_step']
    list_display = ['id', 'fleet', 'low_step', 'serial_number']
    # list_editable = ['low_step', 'serial_number']


admin.site.register(models.Fleet, FleetAdmin)
admin.site.register(models.Steward)
admin.site.register(models.Bike, BikeAdmin)