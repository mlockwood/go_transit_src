from django.contrib import admin

from .models import Metadata, Entry


class EntryInline(admin.TabularInline):
    model = Entry
    extra = 5


class MetadataAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Driver information', {'fields': ['driver', 'login', 'logout']}),
        ('Schedule information', {'fields': ['schedule']}),
        ('Vehicle information', {'fields': ['vehicle', 'start_mileage', 'end_mileage']})
    ]
    inlines = [EntryInline]
    list_display = ('login', 'driver', 'schedule', 'vehicle', 'start_mileage', 'end_mileage', 'logout')
    list_filter = ['driver', 'schedule', 'vehicle']
    search_fields = ['login', 'driver', 'schedule', 'vehicle', 'logout']


admin.site.register(Metadata, MetadataAdmin)
