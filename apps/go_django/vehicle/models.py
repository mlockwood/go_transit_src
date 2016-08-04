from django.db import models


class Vehicle(models.Model):
    license = models.CharField(max_length=12, primary_key=True)
    make = models.CharField(max_length=20, blank=True)
    model = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.license

