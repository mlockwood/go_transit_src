from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from simple_history.models import HistoricalRecords


class Fleet(models.Model):
    id = models.CharField(max_length=12, primary_key=True)
    name = models.CharField(max_length=80)
    description = models.TextField()
    lat = models.DecimalField(max_digits=9, decimal_places=6)
    lng = models.DecimalField(max_digits=9, decimal_places=6)
    operation = models.DateField()
    phone_number = models.CharField(max_length=20)
    schedule = models.TextField(default='24 hours every day except holidays')

    def save(self, *args, **kwargs):
        if self.id is None:
            self.id = self.__class__.objects.all().order_by("-id")[0].id + 1
        super(self.__class__, self).save(*args, **kwargs)


class Steward(models.Model):
    ACTIVE = 'A'
    BACKUP = 'B'
    INACTIVE = 'I'
    STATUS_CHOICES = (
        (ACTIVE, 'The main active bike steward'),
        (BACKUP, 'A designated back-up steward'),
        (INACTIVE, 'The steward is no longer active')
    )
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    phone = PhoneNumberField()
    email = models.EmailField()
    fleet = models.ForeignKey('Fleet')
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    history = HistoricalRecords()


class Bike(models.Model):
    id = models.CharField(max_length=12, primary_key=True)
    serial_number = models.CharField(max_length=40)
    low_step = models.BooleanField()
    fleet = models.ForeignKey('Bike')
    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        if self.id is None:
            self.id = self.__class__.objects.all().order_by("-id")[0].id + 1
        super(self.__class__, self).save(*args, **kwargs)


class GPS(models.Model):
    bike = models.OneToOneField('Bike')
    id = models.CharField(max_length=12, primary_key=True)
    serial_number = models.CharField(max_length=40)
    wi_mm = models.CharField(max_length=40)
    history = HistoricalRecords()


class Lock(models.Model):
    bike = models.OneToOneField('Bike')
    id = models.CharField(max_length=12, primary_key=True)
    serial_number = models.CharField(max_length=40)
    history = HistoricalRecords()


class Asset(models.Model):
    PUMP = 'P'
    TOOLKIT = 'T'
    VEST = 'V'
    ASSET_CHOICES = (
        (PUMP, 'Pump'),
        (TOOLKIT, 'Toolkit'),
        (VEST, 'Vest')
    )
    fleet = models.ForeignKey('Fleet')
    id = models.CharField(max_length=12, primary_key=True)
    asset_type = models.CharField(max_length=1, choices=ASSET_CHOICES)
    history = HistoricalRecords()






