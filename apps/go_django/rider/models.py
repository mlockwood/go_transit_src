from django.db import models

from user.models import EndUser
from stop.models import Stop
from vehicle.models import Vehicle

DATE_INPUT_FORMATS = ('%d%m%Y',)


class Metadata(models.Model):
    schedule = models.IntegerField()
    vehicle = models.ForeignKey('vehicle.Vehicle')
    login = models.DateTimeField(editable=True)
    start_mileage = models.IntegerField()
    end_mileage = models.IntegerField()
    logout = models.DateTimeField(editable=True)

    def __str__(self):
        return 'Metadata {} S{}'.format(self.login, self.schedule)


class Entry(models.Model):
    metadata = models.ForeignKey('Metadata', related_name='entries')
    on = models.ForeignKey('stop.Stop', related_name='on_stop')
    time = models.TimeField(default='12:00:00')
    count = models.IntegerField(default=1)
    off = models.ForeignKey('stop.Stop', related_name='off_stop')

    def __str__(self):
        return '{} riders | On: {} Off: {} @ {}'.format(self.count, self.on, self.off, self.time)

    class Meta:
        unique_together = ('metadata', 'time', 'on', 'off')
        ordering = ['time', 'off']
