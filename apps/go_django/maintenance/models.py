from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from simple_history.models import HistoricalRecords

from bike.models import Bike, BikeGPS, Lock
from fleet.models import FleetAsset
from stop.models import Stop
from vehicle.models import Vehicle


class Damage(models.Model):
    MINOR = 'M'
    REPAIRABLE = 'R'
    SCHEDULED = 'S'
    TOTALED = 'T'
    LOSS = 'L'
    DAMAGE_CHOICES = (
        (MINOR, '(Minor) damage requires attention but does not impact the operation of the asset.'),
        (REPAIRABLE, '(Repairable) damage impacts the operation of the asset but can be repaired.'),
        (SCHEDULED, '(Scheduled) damage caused by normal operation that needs routine maintenance.'),
        (TOTALED, '(Totaled) damage which cannot or should not be repaired and renders the asset unusable.'),
        (LOSS, '(Loss) loss or theft of asset.')
    )
    asset = None  # use models.ForeignKey('class')
    damage = models.CharField(max_length=1, choices=DAMAGE_CHOICES)
    description = models.TextField(blank=True)
    date = models.DateField()

    def __str__(self):
        return '{} for {} on {}'.format(self.damage, self.asset, self.date)


class Inventory(models.Model):
    AVAILABLE = 'A'
    DAMAGED = 'D'
    INSPECT = 'I'
    PASS = 'P'
    SWAP = 'S'
    UNAVAILABLE = 'U'
    CODE_CHOICES = (
        (AVAILABLE, '(A) Asset is in inventory but not deployed/distributed.'),
        (DAMAGED, '(D) Asset shows damage. Follow-up with appropriate damage form.'),
        (INSPECT, '(I) Asset should be inspected by someone trained to assess the asset.'),
        (PASS, '(P) Asset passed inventory level-of-service standards.'),
        (SWAP, '(S) Asset should be swapped out with another asset.'),
        (UNAVAILABLE, '(U) Asset is neither in inventory nor deployed/distributed.'),
    )
    asset = None  # use models.ForeignKey('class')
    timestamp = models.DateTimeField(auto_now_add=True)
    code = models.CharField(max_length=1, choices=CODE_CHOICES)
    notes = models.TextField(blank=True)

    def __str__(self):
        return 'Inventory of {} @ {}'.format(self.asset, self.timestamp)


class Maintenance(models.Model):
    damage_report = None  # use models.ForeignKey('class')
    repair = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    cost = models.DecimalField(max_digits=8, decimal_places=2)
    repair_date = models.DateField()

    def __str__(self):
        return '{} for {} on {}'.format(self.repair, self.asset, self.repair_date)


class BikeDamage(Damage):
    asset = models.ForeignKey('bike.Bike')


class BikeInventory(Inventory):
    asset = models.ForeignKey('bike.Bike')


class BikeMaintenance(Maintenance):
    asset = models.ForeignKey('bike.Bike')
    damage_report = models.ForeignKey('BikeDamage')


class BikeGPSDamage(Damage):
    asset = models.ForeignKey('bike.BikeGPS')


class BikeGPSInventory(Inventory):
    asset = models.ForeignKey('bike.BikeGPS')


class BikeGPSMaintenance(Maintenance):
    asset = models.ForeignKey('bike.BikeGPS')
    damage_report = models.ForeignKey('BikeGPSDamage')


class FleetAssetDamage(Damage):
    asset = models.ForeignKey('fleet.FleetAsset')


class FleetAssetInventory(Inventory):
    asset = models.ForeignKey('fleet.FleetAsset')


class FleetAssetMaintenance(Maintenance):
    asset = models.ForeignKey('fleet.FleetAsset')
    damage_report = models.ForeignKey('FleetAssetDamage')


class LockDamage(Damage):
    asset = models.ForeignKey('bike.Lock')


class LockInventory(Inventory):
    asset = models.ForeignKey('bike.Lock')


class LockMaintenance(Maintenance):
    asset = models.ForeignKey('bike.Lock')
    damage_report = models.ForeignKey('LockDamage')


class StopDamage(Damage):
    asset = models.ForeignKey('stop.Stop')


class StopInventory(Inventory):
    asset = models.ForeignKey('stop.Stop')


class StopMaintenance(Maintenance):
    asset = models.ForeignKey('stop.Stop')
    damage_report = models.ForeignKey('StopDamage')


class VehicleDamage(Damage):
    asset = models.ForeignKey('vehicle.Vehicle')


class VehicleInventory(Inventory):
    asset = models.ForeignKey('vehicle.Vehicle')


class VehicleMaintenance(Maintenance):
    asset = models.ForeignKey('vehicle.Vehicle')
    damage_report = models.ForeignKey('VehicleDamage')
