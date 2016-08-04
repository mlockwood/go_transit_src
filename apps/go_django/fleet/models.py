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
    operating = models.DateField()
    phone = PhoneNumberField()
    schedule = models.TextField(default='24 hours every day except holidays')

    def __str__(self):
        return '({}) {}'.format(self.id, self.name)


class FleetAsset(models.Model):
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

    def __str__(self):
        return '({}) {} - {}: {}'.format(self.fleet.id, self.fleet.name, self.id, self.asset_type)