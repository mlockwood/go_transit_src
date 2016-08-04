from django.contrib import admin
from django.contrib.auth.models import User

from . import models


class EndUserInline(admin.StackedInline):
    model = models.EndUser
    can_delete = False
    verbose_name_plural = 'end users'


class EndUserAdmin(admin.ModelAdmin):
    inlines = (EndUserInline,)


admin.site.unregister(User)
admin.site.register(User, EndUserAdmin)
