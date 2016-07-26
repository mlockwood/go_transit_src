from django.db import models

from driver.models import Driver
from stop.models import Stop
from vehicle.models import Vehicle

DATE_INPUT_FORMATS = ('%d%m%Y',)


class Metadata(models.Model):
    sheet = models.CharField(max_length=20)
    date = models.DateField()
    route = models.CharField(max_length=20)
    driver = models.ForeignKey('driver.Driver')
    vehicle = models.ForeignKey('vehicle.Vehicle')
    login = models.DateTimeField(editable=True)
    start_mileage = models.IntegerField()
    end_mileage = models.IntegerField()
    logout = models.DateTimeField(editable=True)

    def __str__(self):
        return 'Metadata {} S{}'.format(self.date, self.sheet)


class Entry(models.Model):
    metadata = models.ForeignKey('Metadata')
    on = models.ForeignKey('stop.Stop', related_name='on_stop')
    time = models.TimeField()
    count = models.IntegerField()
    off = models.ForeignKey('stop.Stop', related_name='off_stop')

    def __str__(self):
        return '{} riders | On: {} Off: {} @ {}'.format(self.count, self.on, self.off, self.time)
