from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from simple_history.models import HistoricalRecords


from fleet.models import Fleet


class Bike(models.Model):
    id = models.CharField(max_length=12, primary_key=True)
    serial_number = models.CharField(max_length=40)
    low_step = models.BooleanField()
    fleet = models.ForeignKey('fleet.Fleet')
    history = HistoricalRecords()

    def __str__(self):
        return '({}) {} - {}'.format(self.fleet.id, self.fleet.name, self.id)


class BikeGPS(models.Model):
    bike = models.OneToOneField('Bike')
    id = models.CharField(max_length=12, primary_key=True)
    serial_number = models.CharField(max_length=40)
    wi_mm = models.CharField(max_length=40)
    history = HistoricalRecords()

    def __str__(self):
        return '({}) {}'.format(self.bike.id, self.id)


class CheckInOut(models.Model):
    LONG = 'L'
    MEDIUM = 'M'
    SHORT = 'S'
    CHECK_OUT_CHOICES = (
        (LONG, 'Long term check-out up to 30 days.'),
        (MEDIUM, 'Medium term check-out up to 72 hours.'),
        (SHORT, 'Short term check-out up to 12 hours.')
    )
    fleet = models.ForeignKey('fleet.Fleet')
    bike = models.ForeignKey('Bike')
    duration = models.CharField(max_length=1, choices=CHECK_OUT_CHOICES)
    check_out = models.DateTimeField(auto_now_add=True)
    check_in = models.DateTimeField()


class Lock(models.Model):
    bike = models.OneToOneField('Bike')
    id = models.CharField(max_length=12, primary_key=True)
    serial_number = models.CharField(max_length=40)
    history = HistoricalRecords()

    def __str__(self):
        return '({}) {}'.format(self.bike.id, self.id)






