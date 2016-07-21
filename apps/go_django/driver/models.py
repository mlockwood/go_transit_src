from django.db import models


class Driver(models.Model):
    # NEED A PASSWORD FIELD??? CONNECT TO AUTH?
    first = models.CharField(max_length=64)
    last = models.CharField(max_length=64)
    hired = models.DateField()

    def __str__(self):
        return '{}, {}'.format(self.first, self.last)