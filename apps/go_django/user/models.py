from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from simple_history.models import HistoricalRecords

from fleet.models import Fleet


class EndUser(models.Model):
    CURRENT = 'C'
    EXPIRED = 'E'
    NOT_SIGNED = 'N'
    WAIVER_CHOICES = (
        (CURRENT, 'User\'s waiver is currently up-to-date.'),
        (EXPIRED, 'User must sign new waiver agreement.'),
        (NOT_SIGNED, 'User has not signed a waiver.')
    )
    ACTIVE = 'A'
    BACKUP = 'B'
    INACTIVE = 'I'
    NONACTIVE = 'N'
    STATUS_CHOICES = (
        (ACTIVE, 'User is the main active bike steward for their fleet.'),
        (BACKUP, 'User is a designated back-up steward.'),
        (INACTIVE, 'User is no longer an active steward.'),
        (NONACTIVE, 'User has never been a steward.')
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # first_name = models.CharField(max_length=80)
    # last_name = models.CharField(max_length=80)
    # rank = models.CharField(max_length=4, blank=True)
    # phone = PhoneNumberField()
    # email = models.EmailField()
    go_permission = models.IntegerField(default=0)
    transit_staff = models.IntegerField(default=0)
    fleet = models.ForeignKey('fleet.Fleet', null=True, blank=True)
    waiver = models.CharField(max_length=1, choices=WAIVER_CHOICES, default='N')
    waiver_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='N')
    history = HistoricalRecords()
