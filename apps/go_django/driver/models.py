from django.db import models


class Driver(models.Model):
    id = models.CharField(max_length=64, primary_key=True)
    first = models.CharField(max_length=64, blank=True)
    last = models.CharField(max_length=64)
    rank = models.CharField(max_length=4, blank=True)

    def __str__(self):
        return '{}, {}'.format(self.first, self.last)
