from django.contrib import admin

from . import models


class ShelterInline(admin.StackedInline):
    model = models.Shelter
    extra = 0


class SignInline(admin.StackedInline):
    model = models.Sign
    extra = 0


class StopAdmin(admin.ModelAdmin):
    fieldsets = [
        ('General information', {'fields': ['id', 'location', 'location_type', 'name', 'description', 'geography']}),
        ('Coordinate information', {'fields': ['lat', 'lng']}),
        ('Operating information', {'fields': ['operating', 'speed', 'available']})
    ]
    inlines = [ShelterInline, SignInline]
    list_display = ('id', 'name', 'description', 'geography', 'lat', 'lng', 'available')
    list_filter = ['location', 'geography', 'available']
    search_fields = ['id', 'name', 'description', 'geography', 'lat', 'lng', 'available']


admin.site.register(models.Stop, StopAdmin)
admin.site.register(models.Geography)
