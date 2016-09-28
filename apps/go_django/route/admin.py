from django.contrib import admin
import nested_admin

from . import models


class SegmentOrderInline(nested_admin.NestedTabularInline):
    model = models.SegmentOrder
    ordering = ('order',)
    extra = 0


class ScheduleInline(nested_admin.NestedTabularInline):
    model = models.Schedule
    inlines = [SegmentOrderInline]
    ordering = ('id',)
    extra = 0


class JointAdmin(nested_admin.NestedModelAdmin):
    inlines = [ScheduleInline]
    list_filter = ['routes', 'service', 'headway']
    list_display = ['id', 'routes', 'service', 'description', 'headway']
    list_editable = ['routes', 'description', 'headway']


class StopSeqInline(admin.TabularInline):
    model = models.StopSeq
    ordering = ('arrive', 'depart',)
    extra = 0


class SegmentAdmin(admin.ModelAdmin):
    inlines = [StopSeqInline]
    list_filter = ['route', 'direction']
    list_display = ['id', 'route', 'direction', 'description']


admin.site.register(models.Holiday)
admin.site.register(models.Joint, JointAdmin)
admin.site.register(models.Route)
admin.site.register(models.Service)
admin.site.register(models.Segment, SegmentAdmin)
