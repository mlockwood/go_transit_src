import datetime

from django.db import models
from django.utils import timezone


class Driver(models.Model):

    first = models.CharField(max_length=64)
    last = models.CharField(max_length=64)
    hired = models.DateField()

    def __str__(self):
        return '{}, {}'.format(self.first, self.last)


class Stop(models.Model):

    stop_id = models.CharField(max_length=3)
    name = models.CharField(max_length=64)

    def __str__(self):
        return '({}) {}'.format(self.stop_id, self.name)


class Vehicle(models.Model):

    license = models.CharField(max_length=12)
    make = models.CharField(max_length=20)
    model = models.CharField(max_length=20)

    def __str__(self):
        return self.license


class Metadata(models.Model):

    date = models.DateField()
    sheet = models.CharField(max_length=4)
    route = models.CharField(max_length=20)
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    login = models.DateTimeField(editable=True)
    start_mileage = models.IntegerField()
    end_mileage = models.IntegerField()
    logout = models.DateTimeField(editable=True)

    def __str__(self):
        return 'Metadata {} S{}'.format(self.date, self.sheet)


class Data(models.Model):

    metadata = models.ForeignKey(Metadata, on_delete=models.CASCADE)
    on = models.ForeignKey(Stop, related_name='on_stop')
    time = models.TimeField()
    count = models.IntegerField()
    off = models.ForeignKey(Stop, related_name='off_stop')

    def __str__(self):
        return '{} riders | On: {} Off: {} @ {}'.format(self.count, self.on, self.off, self.time)
