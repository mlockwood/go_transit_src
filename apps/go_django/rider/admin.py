from django.contrib import admin

from .models import Metadata, Entry


class EntryInline(admin.TabularInline):
    model = Entry
    extra = 5


class MetadataAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Date information', {'fields': ['date']}),
        ('Schedule information', {'fields': ['sheet', 'route']}),
        ('Driver information', {'fields': ['driver', 'login', 'logout']}),
        ('Vehicle information', {'fields': ['vehicle', 'start_mileage', 'end_mileage']})
    ]
    inlines = [EntryInline]
    list_display = ('date', 'sheet', 'route', 'driver', 'login', 'logout', 'vehicle', 'start_mileage', 'end_mileage')
    list_filter = ['date']
    search_fields = ['date', 'sheet', 'route', 'driver', 'vehicle']


admin.site.register(Metadata, MetadataAdmin)

"""
class DriverAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Name', {'fields': ['last', 'first']}),
        ('GO Profile', {'fields': ['hired']})
    ]
    list_display = ('last', 'first', 'hired')
    list_filter = ['last', 'first', 'hired']
    search_fields = ['last', 'first', 'hired']


class StopAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['stop_id', 'name']}),
    ]
    list_display = ('stop_id', 'name')
    list_filter = ['stop_id', 'name']
    search_fields = ['stop_id', 'name']


class VehicleAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['license', 'make', 'model']}),
    ]
    list_display = ('license', 'make', 'model')
    list_filter = ['license', 'make', 'model']
    search_fields = ['license', 'make', 'model']


admin.site.register(Metadata, MetadataAdmin)
admin.site.register(Driver, DriverAdmin)
admin.site.register(Stop, StopAdmin)
admin.site.register(Vehicle, VehicleAdmin)
"""