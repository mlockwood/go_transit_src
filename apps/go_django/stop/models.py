from django.db import models


class Stop(models.Model):
    stop_id = models.CharField(max_length=3)
    name = models.CharField(max_length=64, default='Unnamed')
    description = models.TextField(blank=True, default='')
    gps_ref = models.CharField(max_length=1)
    geography = models.ForeignKey('Geography')
    lat = models.DecimalField(max_digits=9, decimal_places=6, blank=True)
    lng = models.DecimalField(max_digits=9, decimal_places=6, blank=True)
    signage = models.CharField(max_length=20, default='Undecided')
    shelter = models.CharField(max_length=20, default='Undecided')
    operating = models.DateField()
    speed = models.IntegerField(default=25)
    connections = models.TextField(blank=True, default='')

    class Meta:
        unique_together = ('stop_id', 'gps_ref')

    def __str__(self):
        return '({}) {}'.format(self.stop_id, self.name)


class Geography(models.Model):
    geo_id = models.IntegerField()
    geography = models.CharField(max_length=255)
    min_stop = models.CharField(max_length=3)
    max_stop = models.CharField(max_length=3)


class Inventory(models.Model):
    stop = models.ForeignKey('Stop')
    timestamp = models.DateTimeField(auto_now_add=True)
    code = models.CharField(max_length=1)

