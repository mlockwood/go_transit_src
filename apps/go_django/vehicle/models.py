from django.db import models


class Vehicle(models.Model):
    license = models.CharField(max_length=12, primary_key=True)
    make = models.CharField(max_length=20)
    model = models.CharField(max_length=20)

    def __str__(self):
        return self.license


class Maintenance(models.Model):
    vehicle = models.ForeignKey('Vehicle')
    repair = models.CharField(max_length=100)
    description = models.TextField()
    cost = models.DecimalField(max_digits=8, decimal_places=2)
    repair_date = models.DateField()

    def __str__(self):
        return '{} for vehicle {} on {}'.format(self.repair, self.vehicle, self.repair_date)

