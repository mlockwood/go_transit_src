from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from phonenumber_field.modelfields import PhoneNumberField
from rest_framework.authtoken.models import Token
from simple_history.models import HistoricalRecords

from fleet.models import Fleet


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


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
    id = models.CharField(max_length=80, primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    title_or_rank = models.CharField(max_length=80, blank=True, null=True)
    organization = models.ForeignKey('Organization')
    office_phone = PhoneNumberField(default='+12539663939')
    cell_phone = PhoneNumberField(blank=True, null=True)
    mailing_address = models.CharField(max_length=255, blank=True, null=True)
    role_description = models.TextField(blank=True, null=True)
    waiver = models.CharField(max_length=1, choices=WAIVER_CHOICES, default='N')
    waiver_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='N')
    fleet = models.ForeignKey('fleet.Fleet', null=True, blank=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.id


class Organization(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return '{} - {}'.format(self.name, self.description)
