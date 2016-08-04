from django.contrib import admin

from . import models

admin.site.register(models.Carpool)
admin.site.register(models.DaySchedule)
admin.site.register(models.Vanpool)
