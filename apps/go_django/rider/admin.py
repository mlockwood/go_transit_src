from django.contrib import admin

from .models import Metadata, Entry


class EntryInline(admin.TabularInline):
    model = Entry
    extra = 1


class MetadataAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Schedule information', {'fields': ['schedule', 'login', 'logout']}),
        ('Vehicle information', {'fields': ['vehicle', 'start_mileage', 'end_mileage']})
    ]
    inlines = [EntryInline]
    list_display = ('login', 'schedule', 'vehicle', 'start_mileage', 'end_mileage', 'logout')
    list_filter = ['schedule', 'vehicle']
    search_fields = ['login', 'schedule', 'vehicle', 'logout']


admin.site.register(Metadata, MetadataAdmin)
