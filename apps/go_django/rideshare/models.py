from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from simple_history.models import HistoricalRecords

from agency.models import Agency


class Carpool(models.Model):
    monday = models.ForeignKey('DaySchedule', related_name='carpool_monday')
    tuesday = models.ForeignKey('DaySchedule', related_name='carpool_tuesday')
    wednesday = models.ForeignKey('DaySchedule', related_name='carpool_wednesday')
    thursday = models.ForeignKey('DaySchedule', related_name='carpool_thursday')
    friday = models.ForeignKey('DaySchedule', related_name='carpool_friday')
    saturday = models.ForeignKey('DaySchedule', related_name='carpool_saturday')
    sunday = models.ForeignKey('DaySchedule', related_name='carpool_sunday')
    # EVENTUALLY NEED TO ADD LOCATIONS JSON OBJECT
    license = models.CharField(max_length=12, null=True, blank=True)
    occupancy = models.IntegerField()
    hov_parking = models.BooleanField()


class DaySchedule(models.Model):
    operating = models.BooleanField()
    start = models.TimeField(null=True, blank=True)
    end = models.TimeField(null=True, blank=True)


class Vanpool(models.Model):
    name = models.CharField(max_length=20)
    agency = models.ForeignKey('agency.Agency')
    monday = models.ForeignKey('DaySchedule', related_name='vanpool_monday')
    tuesday = models.ForeignKey('DaySchedule', related_name='vanpool_tuesday')
    wednesday = models.ForeignKey('DaySchedule', related_name='vanpool_wednesday')
    thursday = models.ForeignKey('DaySchedule', related_name='vanpool_thursday')
    friday = models.ForeignKey('DaySchedule', related_name='vanpool_friday')
    saturday = models.ForeignKey('DaySchedule', related_name='vanpool_saturday')
    sunday = models.ForeignKey('DaySchedule', related_name='vanpool_sunday')
    # EVENTUALLY NEED TO ADD LOCATIONS JSON OBJECT
    license = models.CharField(max_length=12, null=True, blank=True)
    occupancy = models.IntegerField()
    hov_parking = models.BooleanField()
