from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from simple_history.models import HistoricalRecords


class Agency(models.Model):
    id = models.IntegerField(primary_key=True)
    lang = models.CharField(max_length=2)
    name = models.CharField(max_length=80)
    phone = PhoneNumberField()
    timezone = models.CharField(max_length=80)
    url = models.URLField()
    history = HistoricalRecords()