from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from simple_history.models import HistoricalRecords


from fleet.models import Fleet


class Bike(models.Model):
    id = models.CharField(max_length=12, primary_key=True)
    serial_number = models.CharField(max_length=40)
    low_step = models.BooleanField(default=False)
    fleet = models.ForeignKey('fleet.Fleet')
    history = HistoricalRecords()

    def __str__(self):
        return '{} @ ({}) {}'.format(self.id, self.fleet.id, self.fleet.name)


class BikeGPS(models.Model):
    bike = models.OneToOneField('Bike')
    id = models.CharField(max_length=12, primary_key=True)
    serial_number = models.CharField(max_length=40)
    wi_mm = models.CharField(max_length=40)
    history = HistoricalRecords()

    def __str__(self):
        return '{} @ {}'.format(self.id, self.bike.id)


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
    name = models.CharField(max_length=40)
    phone = models.CharField(max_length=14)
    email = models.CharField(max_length=40)
    check_out = models.DateTimeField()
    check_in = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return '{} from {} @ {}({})'.format(self.bike, self.fleet, self.check_out, self.duration)


class Lock(models.Model):
    bike = models.OneToOneField('Bike')
    id = models.CharField(max_length=12, primary_key=True)
    serial_number = models.CharField(max_length=40)
    history = HistoricalRecords()

    def __str__(self):
        return '{} @ {}'.format(self.id, self.bike.id)






