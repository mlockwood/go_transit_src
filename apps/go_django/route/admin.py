from django.contrib import admin

from . import models


class ScheduleInline(admin.TabularInline):
    model = models.Schedule


class SegmentInline(admin.TabularInline):
    model = models.Segment


class TransferInline(admin.TabularInline):
    model = models.Transfer


class JointAdmin(admin.ModelAdmin):
    inlines = [ScheduleInline, SegmentInline, TransferInline]
    # list_filter = ['fleet', 'low_step']
    # list_display = ['id', 'fleet', 'low_step', 'serial_number']
    # list_editable = ['low_step', 'serial_number']


admin.site.register(models.Direction)
admin.site.register(models.Holiday)
admin.site.register(models.Joint, JointAdmin)
admin.site.register(models.Service)
admin.site.register(models.StopSeq)
