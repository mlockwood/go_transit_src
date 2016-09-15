from django.contrib import admin
from django.contrib.auth.models import User

from . import models


class EndUserInline(admin.StackedInline):
    model = models.EndUser
    can_delete = False
    verbose_name_plural = 'end users'


class EndUserAdmin(admin.ModelAdmin):
    inlines = (EndUserInline,)
    search_fields = ['groups', 'username', 'first_name', 'last_name', 'staff_status', 'is_active', 'id']
    list_filter = ['is_active']
    list_display = ['username', 'first_name', 'last_name', 'id', 'is_active']


admin.site.unregister(User)
admin.site.register(User, EndUserAdmin)
admin.site.register(models.Organization)
