from django.contrib import admin

from . import models


class AssetInline(admin.StackedInline):
    model = models.FleetAsset


class FleetAdmin(admin.ModelAdmin):
    inlines = [AssetInline]
    search_fields = ['id', 'name', 'description', 'schedule']



admin.site.register(models.Fleet, FleetAdmin)
