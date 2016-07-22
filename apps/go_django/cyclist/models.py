from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from simple_history.models import HistoricalRecords

from bike.models import Bike, Fleet

class Cyclist(models.Model):
    CURRENT = 'C'
    EXPIRED = 'E'
    NOT_SIGNED = 'N'
    WAIVER_CHOICES = (
        (CURRENT, 'User\'s waiver is currently up-to-date.'),
        (EXPIRED, 'User must sign new waiver agreement.'),
        (NOT_SIGNED, 'User has not signed a waiver.')
    )
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    phone = PhoneNumberField()
    email = models.EmailField()
    waiver = WAIVER_CHOICES
    waiver_time = models.DateTimeField()
    history = HistoricalRecords()


class CheckInOut(models.Model):
    LONG = 'L'
    MEDIUM = 'M'
    SHORT = 'S'
    CHECK_OUT_CHOICES = (
        (LONG, 'Long term check-out up to 30 days.'),
        (MEDIUM, 'Medium term check-out up to 72 hours.'),
        (SHORT, 'Short term check-out up to 12 hours.')
    )
    fleet = models.ForeignKey('bike.Fleet')
    bike = models.ForeignKey('bike.Bike')
    duration = models.CharField(max_length=1, choices=CHECK_OUT_CHOICES)
    check_out = models.DateTimeField(auto_now_add=True)
    check_in = models.DateTimeField()
