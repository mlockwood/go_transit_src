from django.contrib import admin

from . import models


class BikeGPSInline(admin.StackedInline):
    model = models.BikeGPS


class LockInline(admin.StackedInline):
    model = models.Lock


class BikeAdmin(admin.ModelAdmin):
    inlines = [BikeGPSInline, LockInline]
    list_filter = ['fleet', 'low_step']
    list_display = ['id', 'fleet', 'low_step', 'serial_number']
    # list_editable = ['low_step', 'serial_number']


admin.site.register(models.Bike, BikeAdmin)
admin.site.register(models.CheckInOut)
